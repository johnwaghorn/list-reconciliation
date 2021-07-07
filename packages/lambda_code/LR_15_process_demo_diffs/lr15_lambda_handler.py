import json
from collections import defaultdict
from typing import Dict, List, Tuple

import boto3
from spine_aws_common.lambda_application import LambdaApplication

from services.jobs import get_job
from utils.datetimezone import get_datetime_now
from utils.logger import success, log_dynamodb_error, UNHANDLED_ERROR
from utils.database.models import JobStats, Jobs, DemographicsDifferences, Demographics
from utils.statuses import JobStatus

MANUAL_VALIDATION = "Manual Validation"

import os

cwd = os.path.dirname(__file__)
ADDITIONAL_LOG_FILE = os.path.join(cwd, "..", "..", "utils/cloudlogbase.cfg")


class DemographicDifferences(LambdaApplication):
    def __init__(self):
        super().__init__(additional_log_config=ADDITIONAL_LOG_FILE)
        self.job_id = None

    def initialise(self):
        pass

    def start(self):

        try:
            self.response = json.dumps(
                self.process_demographic_differences(self.job_id)
            )

        except Exception as err:
            msg = f"Unhandled error getting PDS registrations. JobId: {self.job_id or '99999999-0909-0909-0909-999999999999'}"
            error_response = log_dynamodb_error(
                self.log_object, self.job_id, UNHANDLED_ERROR, msg
            )

            raise Exception(error_response) from err

    @staticmethod
    def create_dsa_payload(
        patient_record: Demographics, demo_diffs: List[DemographicsDifferences]
    ) -> Tuple[Dict, int, int, int, int, int]:
        """Creates a DSA work item payload containing a single patient record with
        one or more demographic differences identified. Determines further actions
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
                    "generalPractitionerOds": patient_record.GP_GpCode,
                },
                "pdsData": {
                    "scn": patient_record.PDS_Version,
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
                    "generalPractitionerOds": patient_record.PDS_GpCode,
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

    def process_demographic_differences(self, job_id: str) -> Dict:
        """Process and output demographic differences for a job, creating DSA work
        item json objects for each patient in a job which has one or more
        demographic differences.

        Args:
            job_id (str): Job id to process

        Returns:
            Dict: Success message including filenames created.
        """

        demo_diffs = DemographicsDifferences.JobIdIndex.query(job_id)

        patients = defaultdict(list)

        for diff in demo_diffs:
            patients[diff.PatientId].append(diff)

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

        job = get_job(job_id)
        practice_code = job.PracticeCode
        now = get_datetime_now().strftime("%Y%m%d%H%M%S")

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

            job_pds_updated += pds_updated
            job_gp_updated += gp_updated
            job_human_validations += human_validations
            job_potential_pds_updates += potential_pds_updates
            job_potential_gp_updates += potential_gp_updates

            key = f"{job_id}/{practice_code}-WIP-{job_id}-{patient_record.NhsNumber}-{now}.json"

            s3 = boto3.client("s3")
            s3.put_object(
                Bucket=self.system_config["MESH_SEND_BUCKET"],
                Key=key,
                Body=json.dumps(dsa_item),
            )
            out_files.append(f"s3://{self.system_config['MESH_SEND_BUCKET']}/{key}")

        self.log_object.write_log(
            "UTI9995",
            None,
            {"logger": "LR15.Lambda", "level": "INFO", "message": "Done"},
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
        job.update(
            actions=[
                Jobs.StatusId.set(JobStatus.DEMOGRAPHICS_DIFFERENCES_PROCESSED.value)
            ]
        )

        self.log_object.write_log(
            "UTI9995",
            None,
            {"logger": "LR15.Lambda", "level": "INFO", "message": "Job updated"},
        )

        out: dict = success(f"Demographic differences processed for JobId {job_id}")
        out.update(filenames=out_files)

        return out
