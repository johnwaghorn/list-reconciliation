import json
import traceback

import boto3
from database import Demographics
from gp_file_parser.utils import empty_string
from lr_logging import Message, error, get_cloudlogbase_config, success
from lr_retry import retry_func
from pds_api.pds_api import PDSAPI, PDSAPIError
from registration import GPRegistrationStatus, get_gp_registration_status
from spine_aws_common.lambda_application import LambdaApplication


class PdsHydrate(LambdaApplication):
    def __init__(self):
        super().__init__(additional_log_config=get_cloudlogbase_config())
        self.api = PDSAPI(self.system_config)
        self.job_id = None
        self.lambda_ = boto3.client("lambda")
        self.s3 = boto3.client("s3")

    def start(self):
        upload_bucket = self.event["Records"][0]["s3"]["bucket"]["name"]
        upload_key = self.event["Records"][0]["s3"]["object"]["key"]

        self.log_object.write_log(
            "LR07I06",
            log_row_dict={
                "file_name": upload_key,
                "bucket": upload_bucket,
            },
        )

        body = json.loads(
            retry_func(
                lambda: self.s3.get_object(Bucket=upload_bucket, Key=upload_key),
                wait_exponential_multiplier=1000,
                wait_exponential_max=10000,
                stop_max_attempt_number=10,
            )["Body"]
            .read()
            .decode("utf-8")
        )

        self.job_id = str(body["job_id"])
        self.log_object.set_internal_id(self.job_id)
        self.log_object.write_log(
            "LR07I05",
            log_row_dict={
                "patient_id": body["id"],
                "nhs_number": body["NHS_NUMBER"],
                "job_id": self.job_id,
            },
        )

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
            self.log_object.write_log(
                "LR07I05",
                log_row_dict={
                    "patient_id": body["id"],
                    "nhs_number": body["NHS_NUMBER"],
                    "job_id": self.job_id,
                },
            )
            self.response = self.pds_hydrate(patient)
            self.response.update({"internal_id": self.log_object.internal_id})

            retry_func(
                lambda: self.s3.delete_object(Bucket=upload_bucket, Key=upload_key),
                wait_exponential_multiplier=1000,
                wait_exponential_max=10000,
                stop_max_attempt_number=10,
            )

        except PDSAPIError as e:
            self.log_object.write_log(
                "LR07C01",
                log_row_dict={
                    "patient_id": patient.Id,
                    "nhs_number": patient.NhsNumber,
                    "job_id": self.job_id,
                    "response_message": traceback.format_exc(),
                },
            )
            self.response = error(
                message="LR07 Lambda error fetching PDS record",
                internal_id=self.log_object.internal_id,
                patient_id=patient.Id,
                nhs_number=patient.NhsNumber,
                job_id=self.job_id,
                error=traceback.format_exc(),
            )
            raise e

        except KeyError as e:
            self.response = error(
                message="LR07 Lambda tried to access missing key",
                internal_id=self.log_object.internal_id,
                error=traceback.format_exc(),
            )
            raise e

        except Exception as e:
            self.response = error(
                message="LR07 Lambda unhandled exception caught",
                internal_id=self.log_object.internal_id,
                error=traceback.format_exc(),
            )
            raise e

    def pds_hydrate(self, record: Demographics) -> Message:
        """Populate an existing Demographics DynamoDB record with PDS data and trigger LR08.

        Returns:
            Message: A dict result containing a status and message
        """
        pds_record = self.api.get_pds_record(record.NhsNumber, self.job_id)

        self.log_object.write_log(
            "LR07I01",
            log_row_dict={
                "patient_id": record.Id,
                "nhs_number": record.NhsNumber,
                "job_id": self.job_id,
            },
        )

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

            self.log_object.write_log(
                "LR07I04",
                log_row_dict={
                    "patient_id": record.Id,
                    "nhs_number": record.NhsNumber,
                    "job_id": self.job_id,
                },
            )

            return success(
                message="LR07 Lambda application stopped",
                internal_id=self.log_object.internal_id,
                job_id=self.job_id,
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

        self.log_object.write_log(
            "LR07I02",
            log_row_dict={"patient_id": record.Id, "job_id": self.job_id},
        )

        self.lambda_.invoke(
            FunctionName=self.system_config["DEMOGRAPHIC_COMPARISON_LAMBDA"],
            InvocationType="Event",
            Payload=json.dumps({"patient_id": record.Id, "job_id": self.job_id}),
        )

        self.log_object.write_log(
            "LR07I03",
            log_row_dict={"job_id": self.job_id},
        )

        return success(
            message="LR07 Lambda application stopped",
            internal_id=self.log_object.internal_id,
            job_id=self.job_id,
        )
