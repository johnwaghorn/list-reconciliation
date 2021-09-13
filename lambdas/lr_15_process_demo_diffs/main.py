from lr_15_process_demo_diffs.lr_15_lambda_handler import DemographicDifferences

app = DemographicDifferences()


def lambda_handler(event, context):
    return app.main(event, context)
