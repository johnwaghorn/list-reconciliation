from lr_08_demographic_comparison.lr_08_lambda_handler import DemographicComparison

app = DemographicComparison()


def lambda_handler(event, context):
    return app.main(event, context)
