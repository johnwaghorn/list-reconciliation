from lambda_code.LR_09_scheduled_check.LR09_lambda_handler import ScheduledCheck

app = ScheduledCheck()


def lambda_handler(event, context):
    return app.main(event, context)
