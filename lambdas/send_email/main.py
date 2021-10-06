from lambda_send_email.lambda_handler import SendEmail

app = SendEmail()


def lambda_handler(event, context):
    return app.main(event, context)
