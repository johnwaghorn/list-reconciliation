def lambda_handler(event, context):
    from validate_and_parse_uploads import validate_and_parse_uploads

    return validate_and_parse_uploads(event, context)
