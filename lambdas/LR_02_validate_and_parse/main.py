from lambda_code.LR_02_validate_and_parse.lr_02_lambda_handler import ValidateAndParse

app = ValidateAndParse()


def lambda_handler(event, context):
    return app.main(event, context)
