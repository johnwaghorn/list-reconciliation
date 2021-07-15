import json
import os

import boto3
from spine_aws_common.lambda_application import LambdaApplication

cwd: str = os.path.dirname(__file__)
ADDITIONAL_LOG_FILE: str = os.path.join(cwd, "..", "..", "utils/cloudlogbase.cfg")


class MeshPostOffice(LambdaApplication):
    def __init__(self):
        super().__init__(additional_log_config=ADDITIONAL_LOG_FILE, load_ssm_params=True)
        self.mappings: dict = json.loads(str(self.system_config["mappings"]))
        self.mesh_post_office_open: str = str(self.system_config["mesh_post_office_open"])

    def start(self):
        if not self.check_if_open():
            # exit early if the Post Office is closed
            # we don't want to deliver any Mesh messages to LR-01 Inbound
            msg = "post_office_status=closed"
            self.log_object.write_log(
                "UTI9995",
                None,
                {
                    "logger": "LR25.Lambda",
                    "level": "INFO",
                    "message": "post_office_status=closed",
                },
            )
            self.response = json.dumps({"msg": msg})
            return

        msg = "post_office_status=open"
        self.log_object.write_log(
            "UTI9995",
            None,
            {
                "logger": "LR25.Lambda",
                "level": "INFO",
                "message": msg,
            },
        )

        # for each mapping picked up from SSM
        for mapping in self.mappings:

            # get all of the messages on the mappings inbound key
            messages = self.get_mesh_messages(
                mapping["inbound"]["bucket"], mapping["inbound"]["key"]
            )

            # move each message to the mappings outbound bucket and key
            for message in messages:
                new_key = message.replace(mapping["inbound"]["key"], mapping["outbound"]["key"])
                self.s3_move_file(
                    old_bucket=mapping["inbound"]["bucket"],
                    old_key=message,
                    new_bucket=mapping["outbound"]["bucket"],
                    new_key=new_key,
                )

        self.response = json.dumps({"msg": msg})
        return

    def get_mesh_messages(self, bucket: str, key: str):
        messages = self.s3_list_files_in_bucket(bucket, key)
        for message in messages:
            self.log_object.write_log(
                "UTI9995",
                None,
                {
                    "logger": "LR25.Lambda",
                    "level": "INFO",
                    "message": f"found message={message}",
                },
            )
        return messages

    def check_if_open(self) -> bool:
        """
        Check to see if the Post Office is open
        """
        if self.mesh_post_office_open == "True":
            return True
        return False

    def s3_move_file(
        self,
        old_bucket: str,
        old_key: str,
        new_bucket: str,
        new_key: str,
        delete_original: bool = True,
    ) -> None:
        """
        Move a file between locations in S3
        """
        s3r = boto3.resource("s3")
        self.log_object.write_log(
            "UTI9995",
            None,
            {
                "logger": "LR25.Lambda",
                "level": "INFO",
                "message": f"moving from file={old_bucket}/{old_key} to file={new_bucket}/{new_key}",
            },
        )
        s3r.Object(new_bucket, new_key).copy_from(
            ACL="bucket-owner-full-control", CopySource={"Bucket": old_bucket, "Key": old_key}
        )
        if delete_original:
            self.log_object.write_log(
                "UTI9995",
                None,
                {
                    "logger": "LR25.Lambda",
                    "level": "INFO",
                    "message": f"deleting original file={old_bucket}/{old_key}",
                },
            )
            s3r.Object(old_bucket, old_key).delete()

    def s3_list_files_in_bucket(self, bucket_name, prefix) -> list:
        """
        List all files in an S3 Bucket
        """
        s3r = boto3.resource("s3")
        bucket = s3r.Bucket(bucket_name)
        all_objects = bucket.objects.all()
        objects = []
        for object in all_objects:
            if object.key.startswith(prefix) and not object.key.endswith("/"):
                objects.append(object.key)
        return objects
