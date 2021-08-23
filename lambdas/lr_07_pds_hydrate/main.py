from lambda_code.lr_07_pds_hydrate.lr_07_lambda_handler import PdsHydrate

app = PdsHydrate()


def lambda_handler(event, context):
    return app.main(event, context)
