from pds_api_mock.main import handler


def lambda_handler(event, context):
    return handler(event, context)
