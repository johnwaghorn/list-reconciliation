from lambda_code.LR_15_process_demo_diffs.lr15_lambda_handler import (
    DemographicDifferences,
)

app = DemographicDifferences()


def lambda_handler(event, context):
    return app.main(event, context)
