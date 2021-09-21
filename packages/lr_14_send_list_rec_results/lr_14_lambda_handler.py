import json
import os
import traceback

import boto3
import nhs_mail_relay
import pytz
from aws.ssm import get_ssm_params
from database.models import DemographicsDifferences, Jobs, JobStats
from lr_logging import get_cloudlogbase_config
from lr_logging.responses import Message, error, success
from mesh import AWSMESHMailbox, get_mesh_mailboxes
from spine_aws_common.lambda_application import LambdaApplication

from .listrec_results_email_template import BODY


class SendListRecResults(LambdaApplication):
    def __init__(self):
        super().__init__(additional_log_config=get_cloudlogbase_config())
        self.send_emails = self.system_config["SEND_EMAILS"] == "true"
        self.mesh_params = get_ssm_params(
            self.system_config["MESH_SSM_PREFIX"], self.system_config["AWS_REGION"]
        )
        self.email_params = get_ssm_params(
            self.system_config["EMAIL_SSM_PREFIX"], self.system_config["AWS_REGION"]
        )
        self.job_id = None
        self.pcse_mesh_id = None

    def initialise(self):
        pass

    def start(self):
        try:
            self.job_id = self.event["job_id"]

            self.log_object.set_internal_id(self.job_id)

            self.response = self.send_list_rec_results()

        except KeyError as e:
            self.response = error(
                "LR14 Lambda tried to access missing key",
                self.log_object.internal_id,
                error=traceback.format_exc(),
            )
            raise e
        except Exception as e:
            self.response = error(
                "LR14 Lambda unhandled exception caught",
                self.log_object.internal_id,
                error=traceback.format_exc(),
            )
            raise e

    def send_list_rec_results(self) -> Message:
        """Send List-Rec results using MESH and email

        Returns:
            Message: A result containing a status and message
        """

        filenames, files = self.get_registration_and_demographic_outputs()

        email_subject, email_body = self.generate_email(filenames)

        self.send_mesh_files(filenames, files)

        self.send_email(email_subject, email_body)

        return success(
            message="LR14 Lambda application stopped",
            internal_id=self.log_object.internal_id,
            to=self.system_config["PCSE_EMAIL"],
            mesh_id=self.pcse_mesh_id,
            email_subject=email_subject,
            email_body=email_body,
            files=filenames,
        )

    def get_registration_and_demographic_outputs(self):
        s3 = boto3.client("s3")

        filenames = [
            os.path.basename(obj["Key"])
            for obj in s3.list_objects_v2(
                Bucket=self.system_config["LR_13_REGISTRATIONS_OUTPUT_BUCKET"],
                Prefix=self.job_id,
            )["Contents"]
        ]

        files = [
            s3.get_object(
                Bucket=self.system_config["LR_13_REGISTRATIONS_OUTPUT_BUCKET"],
                Key=f"{self.job_id}/{filename}",
            )["Body"]
            .read()
            .decode("utf-8")
            for filename in filenames
        ]

        self.log_object.write_log(
            "LR14I01",
            log_row_dict={
                "job_id": self.job_id,
            },
        )

        return filenames, files

    def generate_email(self, filenames: list[str]):
        diffs = list(DemographicsDifferences.JobIdIndex.query(self.job_id))
        unique_patients = {d.PatientId for d in diffs}
        job = Jobs.IdIndex.query(self.job_id).next()
        job_stat = JobStats.get(self.job_id)

        timestamp = job.Timestamp.astimezone(pytz.timezone("Europe/London")).strftime(
            "%H:%M:%S on %d/%m/%Y"
        )
        email_subject = f"PDS Comparison run at {timestamp} against Practice: {job.PracticeCode} - {job.FileName} - Registrations Output"

        filelist = "\n    • ".join(filenames)
        email_body = BODY.format(
            filename=job.FileName,
            timestamp=timestamp,
            only_on_pds=job_stat.OnlyOnPdsRecords,
            only_on_gp=job_stat.OnlyOnGpRecords,
            diffs_count=len(diffs),
            patient_count=len(unique_patients),
            pds_updated_count=job_stat.PdsUpdatedRecords,
            human_validation_count=job_stat.HumanValidationRecords,
            filelist=filelist,
            job_id=self.job_id,
        )

        return email_subject, email_body

    def send_mesh_files(self, filenames: list[str], files: list[str]):
        listrec_mesh_id, pcse_mesh_id = get_mesh_mailboxes(
            json.loads(self.mesh_params["mesh_mappings"]),
            self.mesh_params["listrec_pcse_workflow"],
        )
        self.pcse_mesh_id = pcse_mesh_id

        mesh = AWSMESHMailbox(listrec_mesh_id, self.log_object)
        mesh.send_messages(pcse_mesh_id, zip(filenames, files), overwrite=True)

        self.log_object.write_log(
            "LR14I02",
            log_row_dict={
                "count": len(files),
                "mesh_id": pcse_mesh_id,
                "workflow_id": self.mesh_params["listrec_pcse_workflow"],
                "job_id": self.job_id,
            },
        )

    def send_email(self, subject, body):
        from_address = str(self.system_config["LISTREC_EMAIL"])
        email = {
            "email_addresses": [self.system_config["PCSE_EMAIL"]],
            "subject": subject,
            "message": body,
        }

        if self.send_emails:
            nhs_mail_relay.send_email(
                from_address,
                self.email_params["list_rec_email_password"],
                email,
                self.log_object,
            )
        else:
            self.log_object.write_log(
                "UTI9995",
                None,
                {
                    "logger": "LR14.Lambda",
                    "level": "INFO",
                    "message": f"Email sending={self.send_emails}. Did not send message subject={email['subject']} from={from_address} to={','.join(email['email_addresses'])} with body={email['message']}",
                },
            )

        self.log_object.write_log(
            "LR14I03",
            log_row_dict={
                "receiving_address": [self.system_config["PCSE_EMAIL"]],
                "subject": subject,
                "job_id": self.job_id,
            },
        )
