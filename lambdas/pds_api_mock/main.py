from pds_api_mock.patient import handler


def lambda_handler(event, context):
    return handler(event, context)
