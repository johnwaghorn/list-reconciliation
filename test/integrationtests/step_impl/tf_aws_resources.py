import json
import os

cwd = os.path.dirname(__file__)
OUTPUT_FILE = os.path.join(cwd, "..", "..", "..", "output.json")


def get_aws_resources():
    with open(OUTPUT_FILE) as json_data:
        tf_output = json.load(json_data)
        return tf_output