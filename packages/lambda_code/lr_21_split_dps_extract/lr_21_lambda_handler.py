import os
import json
from datetime import datetime, timedelta

import boto3
from spine_aws_common.lambda_application import LambdaApplication

from utils.exceptions import InvalidPDSData
from utils.logger import success, error, Message

cwd = os.path.dirname(__file__)
ADDITIONAL_LOG_FILE = os.path.join(cwd, "..", "..", "utils/cloudlogbase.cfg")

s3 = boto3.client("s3")
lambda_ = boto3.client("lambda")


class SplitDPSExtract(LambdaApplication):
    def __init__(self):
        super().__init__(additional_log_config=ADDITIONAL_LOG_FILE)
        self.s3 = boto3.client("s3")
        self.input_bucket = self.system_config["LR_20_SUPPLEMENTARY_INPUT_BUCKET"]
        self.output_bucket = self.system_config["LR_22_SUPPLEMENTARY_OUTPUT_BUCKET"]

    def start(self):
        # handle calling from S3 Event or JSON in invoke
        if self.event.get("Records") is not None:
            # pyright: reportOptionalSubscript=false
            dps_data_key = self.event["Records"][0]["s3"]["object"]["key"]
            is_compressed = True if dps_data_key.endswith("gz") else False
            self.s3_event(dps_data_key, is_compressed)
            self.log_object.write_log(
                "LR21I01",
                log_row_dict={
                    "file_name": dps_data_key,
                    "bucket": self.input_bucket,
                },
            )
            self.cleanup_files(
                input_bucket=self.input_bucket,
                input_key=dps_data_key,
                output_bucket=self.output_bucket,
            )
        elif self.event.get("gp_practice") is not None:
            # pyright: reportOptionalSubscript=false
            self.invoked(
                gp_practice=self.event["gp_practice"],
                bucket=self.event["bucket"],
                key=self.event["key"],
                is_compressed=self.event["is_compressed"],
            )
            self.log_object.write_log(
                "LR21I02",
                log_row_dict={
                    "file_name": self.event["key"],
                    "bucket": self.event["bucket"],
                    "gp_practice": self.event["gp_practice"],
                },
            )
        else:
            self.log_object.write_log(
                "LR21W01",
                log_row_dict={
                    "event": self.event,
                },
            )
            raise InvalidPDSData

        self.response = json.dumps({"msg": "LR-21 Completed"})
        return

    def s3_event(self, key: str, is_compressed: bool = True):
        # S3 Select all the gp_practice codes, sadly there's no DISTINCT or UNIQUE available
        s3_select = s3.select_object_content(
            Bucket=self.input_bucket,
            Key=key,
            Expression='SELECT "gp_practice" FROM s3object',
            ExpressionType="SQL",
            InputSerialization={
                "CSV": {
                    "FileHeaderInfo": "USE",
                },
                "CompressionType": "GZIP" if is_compressed else "NONE",
            },
            OutputSerialization={
                "CSV": {
                    "QuoteFields": "ASNEEDED",
                }
            },
        )
        gp_practices = []
        for event in s3_select["Payload"]:
            if "Records" in event:
                for gp_practice in event["Records"]["Payload"].decode("utf-8").splitlines():
                    gp_practices.append(gp_practice)

        # For each GP Practice invoke this Lambda again to split out the data
        for gp_practice in list(set(gp_practices)):
            self.log_object.write_log(
                "LR21I04",
                log_row_dict={
                    "file_name": key,
                    "bucket": self.input_bucket,
                    "gp_practice": gp_practice,
                },
            )
            lambda_.invoke(
                FunctionName=self.context.invoked_function_arn,
                InvocationType="Event",
                Payload=json.dumps(
                    {
                        "gp_practice": gp_practice,
                        "bucket": self.input_bucket,
                        "key": key,
                        "is_compressed": is_compressed,
                    }
                ).encode("utf-8"),
            )

    def invoked(self, gp_practice: str, bucket: str, key: str, is_compressed: bool = True):
        self.log_object.write_log(
            "LR21I05",
            log_row_dict={
                "file_name": key,
                "bucket": bucket,
                "gp_practice": gp_practice,
            },
        )

        # S3 Select the GP Practice data out of the combined file
        s3_select = s3.select_object_content(
            Bucket=bucket,
            Key=key,
            Expression=f"SELECT nhs_number, dispensing_flag FROM s3object s WHERE s.gp_practice = '{gp_practice}'",
            ExpressionType="SQL",
            InputSerialization={
                "CSV": {
                    "FileHeaderInfo": "USE",
                },
                "CompressionType": "GZIP" if is_compressed else "NONE",
            },
            OutputSerialization={
                "CSV": {
                    "QuoteFields": "ASNEEDED",
                }
            },
        )

        # get output stream
        csv_data = b"nhs_number,dispensing_flag\n"
        for event in s3_select["Payload"]:
            if "Records" in event:
                csv_data += event["Records"]["Payload"]

        # write to S3 file named gp_practice
        s3.put_object(Body=csv_data, Bucket=self.output_bucket, Key=f"{gp_practice}.csv")
        self.log_object.write_log(
            "LR21I06",
            log_row_dict={
                "file_name": key,
                "bucket": bucket,
                "gp_practice": gp_practice,
            },
        )

    # TODO: what is the business requirement around this?
    #   Having this delete GP Files after 4 hours will mean unless we recieve new data from DPS every 4 hours, we will have no PDS data to compare against for the GP
    #   However, this cleanup only happens when we recieve a new file, so it may only cleanup when we recieve daily(?) from DPS
    def cleanup_files(
        self, input_bucket: str, input_key: str, output_bucket: str, maximum_age_hours: int = 4
    ):
        """Cleanup any file from the LR-22 output bucket, which haven't been recently modified
        Remove the DSA upload file from LR-20 input bucket"""

        try:
            minimum_last_update = datetime.now() - timedelta(hours=maximum_age_hours)

            # Clean up split out GP Files
            paginator = self.s3.get_paginator("list_objects_v2")
            pages = paginator.paginate(Bucket=output_bucket)
            for page in pages:
                for obj in page.get("Contents", []):
                    mod_date = obj["LastModified"]
                    if mod_date < minimum_last_update:
                        self.s3.delete_object(Bucket=output_bucket, Key=obj["Key"])
                        self.log_object.write_log(
                            "LR21I07",
                            log_row_dict={
                                "file_name": obj["Key"],
                                "bucket": output_bucket,
                            },
                        )

            # Clean up split out PDS Supplementary data file
            paginator = self.s3.get_paginator("list_objects_v2")
            pages = paginator.paginate(Bucket=input_bucket)
            for page in pages:
                for obj in page.get("Contents", []):
                    mod_date = obj["LastModified"]
                    if mod_date < minimum_last_update:
                        self.s3.delete_object(Bucket=input_bucket, Key=obj["Key"])
                        self.log_object.write_log(
                            "LR21I08",
                            log_row_dict={
                                "file_name": obj["Key"],
                                "bucket": input_bucket,
                            },
                        )
        except Exception:
            self.log_object.write_log(
                "LR21W02",
                log_row_dict={
                    "bucket": input_bucket,
                },
            )
