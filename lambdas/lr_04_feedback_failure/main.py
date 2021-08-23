from lambda_code.lr_04_feedback_failure.lr_04_lambda_handler import FeedbackFailure

app = FeedbackFailure()


def lambda_handler(event, context):
    return app.main(event, context)
