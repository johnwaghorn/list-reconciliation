from lr_14_send_list_rec_results.lr_14_lambda_handler import SendListRecResults

app = SendListRecResults()


def lambda_handler(event, context):
    return app.main(event, context)
