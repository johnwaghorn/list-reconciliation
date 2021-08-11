import json
from collections import defaultdict
from typing import Dict, List, Tuple, Any

import boto3
from spine_aws_common.lambda_application import LambdaApplication

from services.aws_mesh import AWSMESHMailbox, get_mesh_mailboxes
from services.jobs import get_job
from utils import write_to_mem_csv
from utils.database.models import JobStats, Jobs, DemographicsDifferences, Demographics
from utils.datetimezone import get_datetime_now
from utils.pds_api_service import SensitiveMarkers
from utils.logger import success, log_dynamodb_error, UNHANDLED_ERROR
from utils.statuses import JobStatus
from utils.ssm import get_ssm_params

MANUAL_VALIDATION = "Manual Validation"


class DemographicDifferences(LambdaApplication):
    def __init__(self):
        super().__init__()
        self.job_id = None
        self.mesh_params = get_ssm_params(
            self.system_config["MESH_SSM_PREFIX"], self.system_config["AWS_REGION"]
        )

    def initialise(self):
        pass

    def start(self):
        try:
            self.job_id = str(self.event["job_id"])

            self.log_object.set_internal_id(self.job_id)

            self.response = json.dumps(self.process_demographic_differences(self.job_id))

        except KeyError as err:
            error_message = f"Lambda event has missing {str(err)} key"
            self.response = {"message": error_message}
            self.log_object.write_log(
                "UTI9995",
                None,
                {
                    "logger": "LR15.Lambda",
                    "level": "INFO",
                    "message": self.response["message"],
                },
            )

        except Exception as err:
            msg = f"Unhandled error getting PDS registrations. JobId: {self.job_id or '99999999-0909-0909-0909-999999999999'}"
            error_response = log_dynamodb_error(self.log_object, self.job_id, UNHANDLED_ERROR, msg)

            raise Exception(error_response) from err

    @staticmethod
    def create_dsa_payload(
        patient_record: Demographics, demo_diffs: List[DemographicsDifferences]
    ) -> Tuple[Dict, int, int, int, int, int]:
        """Creates a DSA work item payload containing a single patient record with
        one or more demographic differences identified.
        Demographic differences list is empty for Sensitive patients
        Determines further actions
        based on rules provided by the listrec_comparison_engine definitions and
        provides counts for the types of actions determined.

        Args:
            patient_record (Dict): The patient record, following the Demographics
                data model in utils.database.models.
            demo_diffs (List[Dict]): The demographic differences following the
                DemographicsDifferences data model in utils.database.models.

        Returns:
            Tuple[Dict, int, int, int, int, int]: (DSA work item, human_validations,
                pds_updated, gp_updated, potential_pds_updates, potential_gp_updates)
        """

        diffs = []

        human_validations = 0
        pds_updated = 0
        gp_updated = 0
        potential_pds_updates = 0
        potential_gp_updates = 0

        for demo_diff in demo_diffs:
            diffs.append(
                {
                    "ruleId": demo_diff.RuleId,
                    "guidance": MANUAL_VALIDATION,
                }
            )

            human_validations += 1

        dsa_item = {
            "system": {
                "name": "GP List Reconciliation",
                "source": "GP System",
                "patientId": patient_record.Id,
                "jobId": patient_record.JobId,
            },
            "patient": {
                "nhsNumber": patient_record.NhsNumber,
                "gpData": {
                    "birthDate": patient_record.GP_DateOfBirth,
                    "gender": patient_record.GP_Gender,
                    "name": {
                        "given": patient_record.GP_Forenames,
                        "family": patient_record.GP_Surname,
                        "previousFamily": patient_record.GP_PreviousSurname,
                        "prefix": patient_record.GP_Title,
                    },
                    "address": {
                        "line1": patient_record.GP_AddressLine1,
                        "line2": patient_record.GP_AddressLine2,
                        "line3": patient_record.GP_AddressLine3,
                        "line4": patient_record.GP_AddressLine4,
                        "line5": patient_record.GP_AddressLine5,
                    },
                    "postalCode": patient_record.GP_PostCode,
                    "generalPractitionerOds": patient_record.GP_GpPracticeCode,
                },
                "pdsData": {
                    "scn": patient_record.PDS_Version,
                    "security": patient_record.PDS_Sensitive,
                    "birthDate": patient_record.PDS_DateOfBirth,
                    "gender": patient_record.PDS_Gender,
                    "name": [
                        {
                            "given": patient_record.PDS_Forenames,
                            "family": patient_record.PDS_Surname,
                            "prefix": patient_record.PDS_Titles,
                        }
                    ],
                    "address": patient_record.PDS_Address,
                    "postalCode": patient_record.PDS_PostCode,
                    "generalPractitionerOds": patient_record.PDS_GpPracticeCode,
                },
            },
            "differences": diffs,
        }

        return (
            dsa_item,
            human_validations,
            pds_updated,
            gp_updated,
            potential_pds_updates,
            potential_gp_updates,
        )

    @staticmethod
    def summarise_dsa_work_item(dsa_work_item: Dict):
        patient = dsa_work_item["patient"]
        summary_record_dict = {
            "nhsNumber": patient["nhsNumber"],
            "gp_birthDate": patient["gpData"]["birthDate"],
            "gp_gender": patient["gpData"]["gender"],
            "gp_name_given": patient["gpData"]["name"]["given"],
            "gp_name_family": patient["gpData"]["name"]["family"],
            "gp_name_previousFamily": patient["gpData"]["name"]["previousFamily"],
            "gp_name_prefix": patient["gpData"]["name"]["prefix"],
            "gp_address_line1": patient["gpData"]["address"]["line1"],
            "gp_address_line2": patient["gpData"]["address"]["line2"],
            "gp_address_line3": patient["gpData"]["address"]["line3"],
            "gp_address_line4": patient["gpData"]["address"]["line4"],
            "gp_address_line5": patient["gpData"]["address"]["line5"],
            "gp_postalCode": patient["gpData"]["postalCode"],
            "gp_generalPractitionerOds": patient["gpData"]["generalPractitionerOds"],
            "pds_scn": patient["pdsData"]["scn"],
            "pds_security": patient["pdsData"]["security"],
            "pds_birthDate": patient["pdsData"]["birthDate"],
            "pds_gender": patient["pdsData"]["gender"],
            "pds_name_given": " ".join(patient["pdsData"]["name"][0]["given"]),
            "pds_name_family": patient["pdsData"]["name"][0]["family"],
            "pds_name_prefix": ",".join(patient["pdsData"]["name"][0]["prefix"]),
            "pds_address": ",".join(patient["pdsData"]["address"]),
            "pds_postalCode": patient["pdsData"]["postalCode"],
            "pds_generalPractitionerOds": patient["pdsData"]["generalPractitionerOds"],
        }
        demographic_diffs = dsa_work_item["differences"]

        if demographic_diffs:
            return [{**summary_record_dict, **difference} for difference in demographic_diffs]
        else:
            # Sensitive patients
            return [{**summary_record_dict, "ruleId": "sensitive", "guidance": "Manual Validation"}]

    def process_demographic_differences(self, job_id: str) -> Dict:
        """Process and output demographic differences for a job, creating DSA work
        item json objects for each patient in a job which has one or more
        demographic differences.

        Args:
            job_id (str): Job id to process

        Returns:
            Dict: Success message including filenames created.
        """

        demographic_diffs = DemographicsDifferences.JobIdIndex.query(job_id)

        patients = defaultdict(list)
        demographic_diffs = DemographicsDifferences.JobIdIndex.query(job_id)
        sensitive_patients = self.process_sensitive_patients(job_id)
        if sensitive_patients:
            patients.update(sensitive_patients)

        for demographic_diff in demographic_diffs:
            patients[demographic_diff.PatientId].append(demographic_diff)

        self.log_object.write_log(
            "UTI9995",
            None,
            {
                "logger": "LR15.Lambda",
                "level": "INFO",
                "message": f"Processing {len(patients)} patients for JobId {job_id}",
            },
        )

        job_pds_updated = 0
        job_gp_updated = 0
        job_human_validations = 0
        job_potential_pds_updates = 0
        job_potential_gp_updates = 0

        out_files = []
        summary_records = []

        job = get_job(job_id)
        practice_code = job.PracticeCode
        now = get_datetime_now().strftime("%Y%m%d%H%M%S")

        listrec_mesh_id, spinedsa_mesh_id = get_mesh_mailboxes(
            json.loads(self.mesh_params["mesh_mappings"]),
            self.mesh_params["listrec_spinedsa_workflow"],
        )

        mesh = AWSMESHMailbox(listrec_mesh_id, self.log_object)
        for patient_id, diff in patients.items():
            patient_record = Demographics.get(patient_id, job_id)
            (
                dsa_item,
                human_validations,
                pds_updated,
                gp_updated,
                potential_pds_updates,
                potential_gp_updates,
            ) = self.create_dsa_payload(patient_record, patients[patient_id])

            summary_records.extend(self.summarise_dsa_work_item(dsa_item))

            job_pds_updated += pds_updated
            job_gp_updated += gp_updated
            job_human_validations += human_validations
            job_potential_pds_updates += potential_pds_updates
            job_potential_gp_updates += potential_gp_updates

            key = f"{practice_code}-WIP-{job_id}-{patient_record.NhsNumber}-{now}.json"
            sent_file = mesh.send_message(
                spinedsa_mesh_id, key, json.dumps(dsa_item), overwrite=True
            )

            out_files.append(sent_file)

        self.log_object.write_log(
            "UTI9995",
            None,
            {
                "logger": "LR15.Lambda",
                "level": "INFO",
                "message": f"Creating summary records for JobId {job_id}",
            },
        )

        header = [
            "nhsNumber",
            "gp_birthDate",
            "gp_gender",
            "gp_name_given",
            "gp_name_family",
            "gp_name_previousFamily",
            "gp_name_prefix",
            "gp_address_line1",
            "gp_address_line2",
            "gp_address_line3",
            "gp_address_line4",
            "gp_address_line5",
            "gp_postalCode",
            "gp_generalPractitionerOds",
            "pds_scn",
            "pds_security",
            "pds_birthDate",
            "pds_gender",
            "pds_name_given",
            "pds_name_family",
            "pds_name_prefix",
            "pds_address",
            "pds_postalCode",
            "pds_generalPractitionerOds",
            "ruleId",
            "guidance",
        ]

        stream = write_to_mem_csv(summary_records, header)
        csv_key = f"{job_id}/{practice_code}-CDD-{now}.csv"
        s3 = boto3.client("s3")
        s3.put_object(
            Body=stream.getvalue(),
            Bucket=self.system_config["LR_13_REGISTRATIONS_OUTPUT_BUCKET"],
            Key=csv_key,
        )

        try:
            job_stat = JobStats.get(job_id)

        except JobStats.DoesNotExist:
            JobStats(
                job_id,
                PdsUpdatedRecords=job_pds_updated,
                GpUpdatedRecords=job_gp_updated,
                HumanValidationRecords=job_human_validations,
                PotentialPdsUpdateRecords=job_potential_pds_updates,
                PotentialGpUpdateRecords=job_potential_gp_updates,
            ).save()

        else:
            job_stat.update(
                actions=[
                    JobStats.PdsUpdatedRecords.set(job_pds_updated),
                    JobStats.GpUpdatedRecords.set(job_gp_updated),
                    JobStats.HumanValidationRecords.set(job_human_validations),
                    JobStats.PotentialPdsUpdateRecords.set(job_potential_pds_updates),
                    JobStats.PotentialGpUpdateRecords.set(job_potential_gp_updates),
                ]
            )
        self.log_object.write_log(
            "UTI9995",
            None,
            {"logger": "LR15.Lambda", "level": "INFO", "message": "Job stats updated"},
        )

        job = get_job(job_id)
        job.update(actions=[Jobs.StatusId.set(JobStatus.DEMOGRAPHICS_DIFFERENCES_PROCESSED.value)])

        self.log_object.write_log(
            "UTI9995",
            None,
            {"logger": "LR15.Lambda", "level": "INFO", "message": "Job updated"},
        )

        out: dict = success(f"Demographic differences processed for JobId {job_id}")
        out.update(
            work_items=out_files,
            summary=f"s3://{self.system_config['LR_13_REGISTRATIONS_OUTPUT_BUCKET']}/{csv_key}",
        )

        return out

    @staticmethod
    def process_sensitive_patients(job_id) -> Dict[str, List[Any]]:
        """
        Get sensitive patient details from Demographic table , the sensitive status could be
        "R","V", "REDACTED"

        Args:
             job_id:str
        Returns:
               dict of Sensitive patients
               { record_id:[] }
        """
        # Sensitive records are not available in Demographics Difference
        # Get them from Demographic table
        sensitive_records = Demographics.JobIdIndex.query(
            job_id,
            filter_condition=(
                (Demographics.PDS_Sensitive == SensitiveMarkers.RESTRICTED.value)
                | (Demographics.PDS_Sensitive == SensitiveMarkers.VERY_RESTRICTED.value)
                | (Demographics.PDS_Sensitive == SensitiveMarkers.REDACTED.value)
            ),
        )
        # Demographic difference list is empty
        if sensitive_records:
            return {records.Id: [] for records in sensitive_records}
        else:
            return
