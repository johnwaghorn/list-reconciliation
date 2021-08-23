from lambda_code.lr_24_save_records_to_s3.lr24_lambda_handler import SaveRecordsToS3

app = SaveRecordsToS3()


def lambda_handler(event, context):
    return app.main(event, context)
