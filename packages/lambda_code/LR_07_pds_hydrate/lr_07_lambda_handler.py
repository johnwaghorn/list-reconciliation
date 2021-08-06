import json

import boto3
from spine_aws_common.lambda_application import LambdaApplication

from gp_file_parser.utils import empty_string
from utils import retry_func
from utils.database.models import Demographics
from utils.logger import log_dynamodb_error, success, Success, UNHANDLED_ERROR
from utils.pds_api_service import PDSAPIError, PDSAPIHelper
from utils.registration_status import get_gp_registration_status, GPRegistrationStatus


class PdsHydrate(LambdaApplication):
    def __init__(self):
        super().__init__()
        self.s3 = boto3.client("s3")
        self.api = PDSAPIHelper(self.system_config)
        self.lambda_ = boto3.client("lambda", region_name=self.system_config["AWS_REGION"])
        self.job_id = None

    def initialise(self):
        pass

    def start(self):
        upload_key = self.event["Records"][0]["s3"]["object"]["key"]

        body = json.loads(
            retry_func(
                lambda: self.s3.get_object(
                    Bucket=self.system_config["LR_06_BUCKET"], Key=upload_key
                ),
                wait_exponential_multiplier=1000,
                wait_exponential_max=10000,
                stop_max_attempt_number=10,
            )["Body"]
            .read()
            .decode("utf-8")
        )

        self.job_id = str(body["job_id"])

        self.log_object.set_internal_id(self.job_id)

        patient = Demographics(
            Id=body["id"],
            JobId=self.job_id,
            NhsNumber=empty_string(body["NHS_NUMBER"]),
            IsComparisonCompleted=False,
            GP_GpPracticeCode=str(body["practice_code"]),
            GP_HaCipher=str(body["TRADING_PARTNER_NHAIS_CIPHER"]),
            GP_TransactionDate=str(body["DATE_OF_DOWNLOAD"][:10].replace("-", "")),
            GP_TransactionTime=str(body["DATE_OF_DOWNLOAD"][11:16].replace(":", "")),
            GP_TransactionId=str(body["TRANS_ID"]),
            GP_Surname=empty_string(body["SURNAME"]),
            GP_Forenames=empty_string(body["FORENAMES"]),
            GP_PreviousSurname=empty_string(body["PREV_SURNAME"]),
            GP_Title=empty_string(body["TITLE"]),
            GP_Gender=empty_string(body["SEX"]),
            GP_DateOfBirth=empty_string(body["DOB"].replace("-", "")),
            GP_AddressLine1=empty_string(body["ADDRESS_LINE1"]),
            GP_AddressLine2=empty_string(body["ADDRESS_LINE2"]),
            GP_AddressLine3=empty_string(body["ADDRESS_LINE3"]),
            GP_AddressLine4=empty_string(body["ADDRESS_LINE4"]),
            GP_AddressLine5=empty_string(body["ADDRESS_LINE5"]),
            GP_PostCode=empty_string(body["POSTCODE"]),
            GP_DrugsDispensedMarker=str(body["DRUGS_DISPENSED_MARKER"]),
        )

        try:
            json.dumps(self.pds_hydrate(patient.JobId, patient))
            retry_func(
                lambda: self.s3.delete_object(
                    Bucket=self.system_config["LR_06_BUCKET"], Key=upload_key
                ),
                wait_exponential_multiplier=1000,
                wait_exponential_max=10000,
                stop_max_attempt_number=10,
            )

        except KeyError as err:
            error_message = f"Lambda event has missing {str(err)} key"
            self.response = {"message": error_message}
            self.log_object.write_log(
                "UTI9995",
                None,
                {
                    "logger": "LR07.Lambda",
                    "level": "INFO",
                    "message": self.response["message"],
                },
            )

        except Exception as err:
            msg = f"Unhandled error JobId: {patient.JobId}, PatientId: {patient.Id} NhsNumber: {patient.NhsNumber}"
            error_response = log_dynamodb_error(
                self.log_object, patient.JobId, UNHANDLED_ERROR, msg
            )

            raise Exception(error_response) from err

        self.response = success(
            f"Processed JobId: {patient.JobId}, PatientId: {patient.Id} NhsNumber: {patient.NhsNumber}"
        )

    def pds_hydrate(self, job_id: str, record: Demographics) -> Success:
        """Populate an existing Demographics DynamoDB record with PDS data and trigger LR08.

        Args:
            job_id (str): ID of the job the comparison is being applied under.
            record (Demographics): Demographics record to process.

        Returns:
            Success

        Raises:
            PDSAPIError: If the PDS FHIR API call fails, the error message contains
                the response content from the API call.
        """

        try:
            pds_record = self.api.get_pds_record(record.NhsNumber, job_id)

        except PDSAPIError as err:
            msg = f"Error fetching PDS record for NHS number {record.NhsNumber}, {str(err)}"
            error_response = log_dynamodb_error(self.log_object, job_id, str(err), msg)

            raise PDSAPIError(json.dumps(error_response)) from err

        status = get_gp_registration_status(record.GP_GpPracticeCode, pds_record)

        if status == GPRegistrationStatus.UNMATCHED.value:
            record.IsComparisonCompleted = True
            record.GP_RegistrationStatus = status

            retry_func(
                lambda: record.save(),
                wait_exponential_multiplier=1000,
                wait_exponential_max=10000,
                stop_max_attempt_number=10,
            )

            return success(
                f"PDS data not found for JobId: {job_id}, PatientId: {record.Id}, NhsNumber: {record.NhsNumber}"
            )

        retry_func(
            lambda: record.save(),
            wait_exponential_multiplier=1000,
            wait_exponential_max=10000,
            stop_max_attempt_number=10,
        )
        record.update(
            actions=[
                Demographics.PDS_GpPracticeCode.set(pds_record["gp_practicecode"]),
                Demographics.PDS_GpRegisteredDate.set(pds_record["gp_registered_date"]),
                Demographics.PDS_Surname.set(pds_record["surname"]),
                Demographics.PDS_Forenames.set(pds_record["forenames"]),
                Demographics.PDS_Titles.set(pds_record["title"]),
                Demographics.PDS_Gender.set(pds_record["gender"]),
                Demographics.PDS_DateOfBirth.set(pds_record["date_of_birth"]),
                Demographics.PDS_Sensitive.set(pds_record["sensitive"]),
                Demographics.PDS_Address.set(pds_record["address"]),
                Demographics.PDS_PostCode.set(pds_record["postcode"]),
                Demographics.GP_RegistrationStatus.set(status),
                Demographics.PDS_Version.set(pds_record["version"]),
            ]
        )

        self.lambda_.invoke(
            FunctionName=self.system_config["DEMOGRAPHIC_COMPARISON_LAMBDA"],
            InvocationType="Event",
            Payload=json.dumps({"patient_id": record.Id, "job_id": job_id}),
        )

        self.response = success(
            f"Retrieved PDS data for JobId: {job_id}, PatientId: {record.Id}, NhsNumber: {record.NhsNumber}"
        )

        self.log_object.write_log(
            "UTI9995",
            None,
            {
                "logger": "LR07.Lambda",
                "level": "INFO",
                "message": json.dumps(self.response),
            },
        )

        return self.response
