import json

from utils.logger import log_dynamodb_error, UNHANDLED_ERROR


def lambda_handler(event, context):
    from demographic_comparison import demographic_comparisons

    job_id = str(event["job_id"])
    patient_id = str(event["patient_id"])

    try:
        return json.dumps(demographic_comparisons(job_id, patient_id))

    except Exception as err:
        msg = f"Unhandled error patient_id: {patient_id}"
        error_response = log_dynamodb_error(job_id, UNHANDLED_ERROR, msg)

        raise type(err)(error_response) from err
