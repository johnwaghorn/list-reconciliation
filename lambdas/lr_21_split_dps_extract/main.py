from lr_21_split_dps_extract.lr_21_lambda_handler import SplitDPSExtract

app = SplitDPSExtract()


def lambda_handler(event, context):
    return app.main(event, context)
