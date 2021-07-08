from lambda_code.LR_02_validate_and_parse.lr_02_lambda_handler import LR02LambdaHandler

app = LR02LambdaHandler()


def lambda_handler(event, context):
    return app.main(event, context)
