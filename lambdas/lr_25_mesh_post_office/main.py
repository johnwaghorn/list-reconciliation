from lambda_code.lr_25_mesh_post_office.lr_25_lambda_handler import MeshPostOffice

app = MeshPostOffice()


def lambda_handler(event, context):
    return app.main(event, context)
