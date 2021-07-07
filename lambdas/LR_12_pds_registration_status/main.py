from lambda_code.LR_12_pds_registration_status.LR12_lambda_handler import (
    PDSRegistrationStatus,
)

app = PDSRegistrationStatus()


def lambda_handler(event, context):
    return app.main(event, context)
