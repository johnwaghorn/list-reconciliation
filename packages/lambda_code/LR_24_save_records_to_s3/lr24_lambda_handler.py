import json
import sys
import traceback

import boto3
from spine_aws_common.lambda_application import LambdaApplication

from utils import retry_func

S3 = boto3.client("s3")


class SaveRecordsToS3(LambdaApplication):
    def __init__(self):
        super().__init__()

    def initialise(self):
        pass

    def start(self):
        self.log_object.set_internal_id(self._create_new_internal_id())

        records = self.event["records"]
        destination_bucket = self.event["destination_bucket"]
        id_cols = self.event["id_cols"]
        source = self.event["source"]

        self.log_object.write_log(
            "UTI9995",
            None,
            {
                "logger": "LR24.Lambda",
                "level": "INFO",
                "message": f"Splitting {source} {len(records)} records",
            },
        )
        for record in records:
            record_dict = json.loads(record)
            id_ = "id not set"

            try:
                id_ = "_".join([str(record_dict[col]) for col in id_cols])
                retry_func(
                    lambda: S3.put_object(
                        Bucket=destination_bucket,
                        Key=f"{id_}/{id_}.json",
                        Body=json.dumps(record_dict),
                    ),
                    wait_exponential_multiplier=1000,
                    wait_exponential_max=10000,
                    stop_max_attempt_number=10,
                )

            except Exception:
                msg = f"Unhandled error from {source}. {', '.join(id_cols)}: {id_}"
                self.log_object.write_log(
                    "UTI9998",
                    sys.exc_info(),
                    {
                        "logger": "LR24.Lambda",
                        "level": "ERROR",
                        "message": msg,
                    },
                )
                self.response = f"{msg}\n{traceback.format_exc()}"
                return

        self.response = f"Processed {source} {len(records)} records"
        self.log_object.write_log(
            "UTI9995",
            None,
            {
                "logger": "LR24.Lambda",
                "level": "INFO",
                "message": self.response,
            },
        )
