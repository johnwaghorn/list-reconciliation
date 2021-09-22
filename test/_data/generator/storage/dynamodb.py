import csv
import os

import boto3


class DynamoDBStorage:
    def list(self):
        pass

    def store(self, tmp_file):
        dynamodb = boto3.resource("dynamodb")

        # TODO set name once
        # TODO ensure table exists
        # table = dynamodb.create_table(
        #     TableName="pds-api-mock",
        #     KeySchema=[
        #         {"AttributeName": "nhs_number", "KeyType": "HASH"},
        #     ],
        #     AttributeDefinitions=[
        #         {"AttributeName": "nhs_number", "AttributeType": "S"},
        #     ],
        #     ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        # )
        # table.meta.client.get_waiter("table_exists").wait(TableName="pds-api-mock")

        table = dynamodb.Table("pds-api-mock")

        with open(tmp_file) as data:
            with table.batch_writer() as batch:
                for row in csv.DictReader(data):
                    batch.put_item(
                        Item={
                            "nhs_number": row["NHS_NUMBER"],
                            "date_of_birth": row["DATE_OF_BIRTH"],
                            "date_of_death": row["DATE_OF_DEATH"],
                            "family_name": row["FAMILY_NAME"],
                            "given_name": row["GIVEN_NAME"],
                            "other_given_name": row["OTHER_GIVEN_NAME"],
                            "title": row["TITLE"],
                            "gender": row["GENDER"],
                            "address_line_1": row["ADDRESS_LINE_1"],
                            "address_line_2": row["ADDRESS_LINE_2"],
                            "address_line_3": row["ADDRESS_LINE_3"],
                            "address_line_4": row["ADDRESS_LINE_4"],
                            "address_line_5": row["ADDRESS_LINE_5"],
                            "paf_key": row["PAF_KEY"],
                            "sensitive_flag": row["SENSITIVE_FLAG"],
                            "primary_care_code": row["PRIMARY_CARE_CODE"],
                            "ref_id": row["REF_ID"],
                            "post_code": row["POST_CODE"],
                            "dispensing_flag": row["DISPENSING_FLAG"],
                        }
                    )

        os.remove(tmp_file)

    def retrieve(self, data):
        pass
