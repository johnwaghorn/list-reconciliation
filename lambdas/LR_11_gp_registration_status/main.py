from lambda_code.LR_11_gp_registration_status.LR011_lambda_handler import (
    GPRegistrations,
)

app = GPRegistrations()


def lambda_handler(event, context):
    return app.main(event, context)
