from typing import List

import json
import os

import boto3

from spine_aws_common.lambda_application import LambdaApplication

from .listrec_results_email_template import BODY
from utils.logger import success
from utils.database.models import Jobs, DemographicsDifferences, JobStats
from utils.ssm import get_ssm_params
from services.aws_mesh import AWSMESHMailbox, get_mesh_mailboxes

import services.send_email_exchangelib


class SendListRecResults(LambdaApplication):
    def __init__(self):
        super().__init__()
        self.mesh_params = get_ssm_params(
            self.system_config["MESH_SSM_PREFIX"], self.system_config["AWS_REGION"]
        )

        self.email_params = get_ssm_params(
            self.system_config["EMAIL_SSM_PREFIX"], self.system_config["AWS_REGION"]
        )
        self.pcse_mesh_id = None

    def initialise(self):
        pass

    def get_registration_and_demographic_outputs(self):
        self.log_object.write_log(
            "UTI9995",
            None,
            {
                "logger": "LR14.Lambda",
                "level": "INFO",
                "message": f"Gathering files to send results for JobId {self.job_id}",
            },
        )

        s3 = boto3.client("s3")
        filenames = [
            os.path.basename(obj["Key"])
            for obj in s3.list_objects_v2(
                Bucket=self.system_config["LR_13_REGISTRATIONS_OUTPUT_BUCKET"], Prefix=self.job_id
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

        return filenames, files

    def generate_email(self, filenames: List[str]):
        diffs = list(DemographicsDifferences.JobIdIndex.query(self.job_id))
        unique_patients = {d.PatientId for d in diffs}
        job = Jobs.IdIndex.query(self.job_id).next()
        job_stat = JobStats.get(self.job_id)

        timestamp = job.Timestamp.strftime("%H:%M:%S on %d/%m/%Y")
        email_subject = f"PDS Comparison run at {timestamp} against Practice: {job.PracticeCode} - {job.FileName} - Registrations Output"

        filelist = "\n    - ".join(filenames)
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

        self.log_object.write_log(
            "UTI9995",
            None,
            {
                "logger": "LR14.Lambda",
                "level": "INFO",
                "message": email_subject + "\n" + email_body,
            },
        )

        return email_subject, email_body

    def send_mesh_files(self, filenames: List[str], files: List[str]):
        listrec_mesh_id, pcse_mesh_id = get_mesh_mailboxes(
            json.loads(self.mesh_params["mesh_mappings"]),
            self.mesh_params["listrec_pcse_workflow"],
        )
        self.pcse_mesh_id = pcse_mesh_id

        self.log_object.write_log(
            "UTI9995",
            None,
            {
                "logger": "LR14.Lambda",
                "level": "INFO",
                "message": f"Sending files via MESH to {pcse_mesh_id}",
            },
        )
        mesh = AWSMESHMailbox(listrec_mesh_id, self.log_object)
        mesh.send_messages(pcse_mesh_id, zip(filenames, files), overwrite=True)

    def send_email(self, subject, body):
        self.log_object.write_log(
            "UTI9995",
            None,
            {
                "logger": "LR14.Lambda",
                "level": "INFO",
                "message": f"Sending email from {self.system_config['LISTREC_EMAIL']} to {self.system_config['PCSE_EMAIL']}",
            },
        )
        services.send_email_exchangelib.send_exchange_email(
            self.system_config["LISTREC_EMAIL"],
            self.email_params["list_rec_email_password"],
            {
                "email_addresses": [self.system_config["PCSE_EMAIL"]],
                "subject": subject,
                "message": body,
            },
        )

    def start(self):
        self.job_id = self.event["job_id"]

        filenames, files = self.get_registration_and_demographic_outputs()

        email_subject, email_body = self.generate_email(filenames)

        self.send_mesh_files(filenames, files)

        self.send_email(email_subject, email_body)

        self.response = success(
            f"Email and files sent to {self.system_config['PCSE_EMAIL']}, MESH: {self.pcse_mesh_id}"
        )
        self.response.update(email_subject=email_subject, email_body=email_body, files=filenames)
