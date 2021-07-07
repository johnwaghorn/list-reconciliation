from lambda_code.LR_21_split_dps_extract.lr21_lambda_handler import SplitDPSExtract

app = SplitDPSExtract()


def lambda_handler(event, context):
    return app.main(event, context)
