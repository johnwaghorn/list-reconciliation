import json
import traceback

import boto3
from lr_logging import get_cloudlogbase_config
from lr_logging.responses import error, success
from lr_retry import retry_func
from spine_aws_common.lambda_application import LambdaApplication


class SaveRecordsToS3(LambdaApplication):
    def __init__(self):
        self.s3 = boto3.client("s3")
        super().__init__(additional_log_config=get_cloudlogbase_config())

    def initialise(self):
        pass

    def start(self):
        try:
            records = self.event["records"]
            destination_bucket = self.event["destination_bucket"]
            id_cols = self.event["id_cols"]
            source = self.event["source"]

            self.log_object.write_log(
                "LR24I01",
                log_row_dict={
                    "count": len(records),
                    "source": source,
                    "bucket": destination_bucket,
                },
            )

        except KeyError as e:
            self.response = error(
                "LR24 Lambda tried to access missing key",
                self.log_object.internal_id,
                error=traceback.format_exc(),
            )
            raise e

        else:
            for record in records:
                record_dict = json.loads(record)
                id_ = "id not set"

                try:
                    id_ = "_".join([str(record_dict[col]) for col in id_cols])

                    retry_func(
                        lambda: self.s3.put_object(
                            Bucket=destination_bucket,
                            Key=f"{id_}/{id_}.json",
                            Body=json.dumps(record_dict),
                        ),
                        wait_exponential_multiplier=1000,
                        wait_exponential_max=10000,
                        stop_max_attempt_number=10,
                    )

                    self.log_object.write_log(
                        "LR24I02",
                        log_row_dict={
                            "id": id_,
                            "bucket": destination_bucket,
                            "source": source,
                        },
                    )

                except Exception as e:
                    self.log_object.write_log(
                        "LR24C01",
                        log_row_dict={
                            "id": id_,
                            "bucket": destination_bucket,
                            "source": source,
                            "error": traceback.format_exc(),
                        },
                    )
                    self.response = error(
                        f"Unhandled exception in LR24 Lambda with error={traceback.format_exc()}",
                        self.log_object.internal_id,
                    )
                    raise e

            self.log_object.write_log(
                "LR24I03",
                log_row_dict={
                    "count": len(records),
                    "source": source,
                    "bucket": destination_bucket,
                },
            )

            self.response = success(
                message="LR24 Lambda application stopped",
                internal_id=self.log_object.internal_id,
            )
