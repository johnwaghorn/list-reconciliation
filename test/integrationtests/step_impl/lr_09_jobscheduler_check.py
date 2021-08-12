from getgauge.python import step, Messages
import boto3
import json
import base64


from .tf_aws_resources import get_terraform_output

REGION_NAME = "eu-west-2"
LR_09_LAMBDA_ARN = get_terraform_output("lr_09_lambda")


@step("trigger lr09 and expected statuscode is <expstatuscode>")
def trigger_lr09(expstatuscode):
    client = boto3.client("lambda", REGION_NAME)
    response = client.invoke(FunctionName=LR_09_LAMBDA_ARN, LogType="Tail", Payload=json.dumps({}))
    for key, value in response.items():
        if key == "ResponseMetadata":
            assert response["ResponseMetadata"]["HTTPStatusCode"] == int(expstatuscode)


@step("trigger lr09 and ensure scheduled checked successfully completed")
def trigger_lr09_get_requestid():
    client = boto3.client("lambda", REGION_NAME)
    response = client.invoke(FunctionName=LR_09_LAMBDA_ARN, LogType="Tail", Payload="{}")

    for key, value in response.items():
        if key == "ResponseMetadata":
            request_id = response["ResponseMetadata"]["RequestId"]
            tail_output = base64.b64decode(
                response["ResponseMetadata"]["HTTPHeaders"]["x-amz-log-result"]
            )
            log_output = tail_output.decode("utf-8")
            expected_line = "Scheduled checked successfully completed"

            try:
                log_output.index(expected_line)
            except ValueError:
                Messages.write_message("LR-09 scheduled check Unsucessfull")
            else:
                Messages.write_message("LR-09 scheduled check sucessfully completed")

        return request_id
