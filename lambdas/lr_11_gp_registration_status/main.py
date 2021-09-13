from lr_11_gp_registration_status.lr_11_lambda_handler import (
    GPRegistrations,
)

app = GPRegistrations()


def lambda_handler(event, context):
    return app.main(event, context)
