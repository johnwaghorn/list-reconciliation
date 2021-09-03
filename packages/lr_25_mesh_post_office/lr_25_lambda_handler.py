import json
import traceback

import boto3
from lr_logging import get_cloudlogbase_config
from lr_logging.responses import Message, error, success
from spine_aws_common.lambda_application import LambdaApplication


class MeshPostOffice(LambdaApplication):
    def __init__(self):
        super().__init__(
            additional_log_config=get_cloudlogbase_config(), load_ssm_params=True
        )
        self.s3 = boto3.resource("s3")
        self.mappings: dict = json.loads(str(self.system_config["mappings"]))
        self.mesh_post_office_open: str = str(
            self.system_config["mesh_post_office_open"]
        )

    def start(self):
        try:
            self.log_object.set_internal_id(self._create_new_internal_id())

            self.response = self.process_post_office()

        except KeyError as e:
            self.response = error(
                "LR25 Lambda tried to access missing key",
                self.log_object.internal_id,
                error=traceback.format_exc(),
            )
            raise e
        except Exception as e:
            self.response = error(
                "LR25 Lambda unhandled exception caught",
                self.log_object.internal_id,
                error=traceback.format_exc(),
            )
            raise e

    def process_post_office(self) -> Message:
        """Handles post office process

        Returns:
            Message: A dict result containing a status and message
        """

        if not self.check_if_open():
            # exit early if the Post Office is closed
            # we don't want to deliver any Mesh messages to LR-01 Inbound
            self.log_object.write_log(
                "LR25I01",
                log_row_dict={
                    "post_office_status": "closed",
                },
            )

            return success(
                message="LR25 Lambda application stopped",
                internal_id=self.log_object.internal_id,
            )

        # for each mapping picked up from SSM
        for mapping in self.mappings:

            # get all of the messages on the mappings inbound key
            messages = self.get_mesh_messages(
                mapping["inbound"]["bucket"], mapping["inbound"]["key"]
            )

            # move each message to the mappings outbound bucket and key
            for message in messages:
                new_key = message.replace(
                    mapping["inbound"]["key"], mapping["outbound"]["key"]
                )
                self.s3_move_file(
                    old_bucket=mapping["inbound"]["bucket"],
                    old_key=message,
                    new_bucket=mapping["outbound"]["bucket"],
                    new_key=new_key,
                )

        self.log_object.write_log(
            "LR25I01",
            log_row_dict={
                "post_office_status": "open",
            },
        )

        return success(
            message="LR25 Lambda application stopped",
            internal_id=self.log_object.internal_id,
        )

    def get_mesh_messages(self, bucket: str, key: str):
        messages = self.s3_list_files_in_bucket(bucket, key)

        for message in messages:
            self.log_object.write_log(
                "LR25I02",
                log_row_dict={"message": {message}},
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

        self.log_object.write_log(
            "LR25I03",
            log_row_dict={
                "old_key": {old_key},
                "old_bucket": {old_bucket},
                "new_bucket": {new_bucket},
                "new_key": {new_key},
            },
        )

        self.s3.Object(new_bucket, new_key).copy_from(
            ACL="bucket-owner-full-control",
            CopySource={"Bucket": old_bucket, "Key": old_key},
        )

        if delete_original:
            self.log_object.write_log(
                "LR25I04",
                log_row_dict={"file_name": old_key, "bucket": old_bucket},
            )

            self.s3.Object(old_bucket, old_key).delete()

    def s3_list_files_in_bucket(self, bucket_name, prefix) -> list:
        """
        List all files in an S3 Bucket
        """

        bucket = self.s3.Bucket(bucket_name)
        all_objects = bucket.objects.all()

        objects = []
        for object in all_objects:
            if object.key.startswith(prefix) and not object.key.endswith("/"):
                objects.append(object.key)

        return objects
