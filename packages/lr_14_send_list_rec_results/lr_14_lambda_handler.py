import json
import os
import traceback
import uuid

import boto3
import pytz
from aws.ssm import get_ssm_params
from database import DemographicsDifferences, Jobs, JobStats
from lr_logging import get_cloudlogbase_config
from lr_logging.exceptions import SendEmailError
from lr_logging.responses import Message, error, success
from mesh import AWSMESHMailbox, get_mesh_mailboxes
from send_email.send import to_outbox
from spine_aws_common.lambda_application import LambdaApplication

from .listrec_results_email_template import BODY


class SendListRecResults(LambdaApplication):
    def __init__(self):
        super().__init__(additional_log_config=get_cloudlogbase_config())
        self.send_emails = self.system_config["SEND_EMAILS"] == "true"
        self.mesh_params = get_ssm_params(
            self.system_config["MESH_SSM_PREFIX"], self.system_config["AWS_REGION"]
        )
        self.outbox_bucket = self.system_config["AWS_S3_SEND_EMAIL_BUCKET"]
        self.to = self.system_config["PCSE_EMAIL"]
        self.job_id = None
        self.pcse_mesh_id = None
        self.job = None

    def initialise(self):
        pass

    def start(self):
        try:
            self.job_id = self.event["job_id"]

            self.log_object.set_internal_id(self.job_id)

            self.response = self.send_list_rec_results()

        except SendEmailError as e:
            self.log_object.write_log(
                "LR14C01",
                log_row_dict={
                    "email_address": self.to,
                    "job_id": self.job_id,
                    "error": traceback.format_exc(),
                },
            )
            self.response = error(
                message="LR14 Lambda failed to relay email via the send_email package",
                internal_id=self.log_object.internal_id,
                error=traceback.format_exc(),
            )
            raise e

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

        sent = self.send_email(email_subject, email_body)

        if sent:
            return success(
                message="LR14 Lambda application stopped",
                internal_id=self.log_object.internal_id,
                to=self.to,
                mesh_id=self.pcse_mesh_id,
                email_subject=email_subject,
                email_body=email_body,
                files=filenames,
            )

        return error(
            message="LR14 Lambda failed to send list rec results",
            internal_id=self.log_object.internal_id,
            to=self.to,
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
        try:
            self.job = Jobs.IdIndex.query(self.job_id).next()
            self.log_object.write_log(
                "LR14I04",
                log_row_dict={
                    "job_id": self.job_id,
                },
            )
        except:
            self.log_object.write_log(
                "LR14C02",
                log_row_dict={
                    "job_id": self.job_id,
                },
            )
        job_stat = JobStats.get(self.job_id)

        timestamp = self.job.Timestamp.astimezone(
            pytz.timezone("Europe/London")
        ).strftime("%H:%M:%S on %d/%m/%Y")
        email_subject = f"PDS Comparison run at {timestamp} against Practice: {self.job.PracticeCode} - {self.job.FileName} - Registrations Output"

        filelist = "\n    • ".join(filenames)
        email_body = BODY.format(
            filename=self.job.FileName,
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

        service = "LR-14"
        to = self.to
        outbox_filename = str(uuid.uuid4())
        bucket = self.outbox_bucket

        if self.send_emails:
            try:
                sent = to_outbox(service, [to], subject, body, outbox_filename, bucket)

                self.log_object.write_log(
                    "LR14I03",
                    log_row_dict={
                        "email_address": self.to,
                        "subject": subject,
                        "job_id": self.job_id,
                        "outbox_filename": outbox_filename,
                    },
                )
                return sent
            except:
                raise SendEmailError(
                    f"Failed to send email with subject='{subject}' to='{to} for job='{self.job_id}'"
                )

        self.log_object.write_log(
            "LR14W01",
            log_row_dict={
                "sending": self.send_emails,
                "subject": subject,
                "to": self.to,
                "job_id": self.job_id,
            },
        )
