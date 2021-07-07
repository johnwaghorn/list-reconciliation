import json
import os
import sys
from uuid import uuid4

from spine_aws_common.lambda_application import LambdaApplication

from .lr_02_functions import ValidateAndParse

cwd = os.path.dirname(__file__)
ADDITIONAL_LOG_FILE = os.path.join(cwd, "..", "..", "utils/cloudlogbase.cfg")


class LR02LambdaHandler(LambdaApplication):
    def __init__(self):
        super().__init__(additional_log_config=ADDITIONAL_LOG_FILE)
        self.job_id = None
        self.upload_key = None

    def initialise(self):
        self.job_id = str(uuid4())

    def start(self):
        try:
            self.upload_key = self.event["Records"][0]["s3"]["object"]["key"]
            lr02 = ValidateAndParse(
                upload_key=self.upload_key,
                job_id=self.job_id,
                lambda_env=self.system_config,
                logger=self.log_object,
            )
            self.response = lr02.validate_and_process_extract()

            self.log_object.write_log(
                "UTI9995",
                None,
                {
                    "logger": "LR02.Lambda",
                    "level": "INFO",
                    "message": json.dumps(self.response),
                },
            )
        except KeyError as err:
            error_message = f"Lambda event has missing {str(err)} key"
            self.log_object.write_log(
                "UTI9998",
                sys.exc_info(),
                {
                    "logger": "LR02.Lambda",
                    "level": "ERROR",
                    "message": error_message,
                },
            )
            self.response = {"message": error_message}

        except Exception as err:
            self.log_object.write_log(
                "UTI9998",
                sys.exc_info(),
                {
                    "logger": "LR02.Lambda",
                    "level": "ERROR",
                    "message": str(err),
                },
            )
            self.response = {"message": str(err)}
