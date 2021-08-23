from lambda_code.lr_27_job_cleanup.lr_27_lambda_handler import JobCleanup

app = JobCleanup()


def lambda_handler(event, context):
    return app.main(event, context)
