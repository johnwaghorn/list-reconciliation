import json
import os

from getgauge.python import Messages

cwd = os.path.dirname(__file__)
OUTPUT_FILE = os.path.join(cwd, "..", "..", "..", "terraform_outputs_list-reconciliation.json")


def get_aws_resources():
    with open(OUTPUT_FILE) as json_data:
        tf_output = json.load(json_data)
        return tf_output


def get_terraform_output(resource):
    try:
        outputs = {k: v["value"] for k, v in json.load(open(OUTPUT_FILE)).items()}
        return outputs[resource]
    except KeyError:
        # Return the resource name, in place of the value as when Gauge hits issues with missing mappings
        # it exits non-gracefully and gives no hint to the user as to which variable is missing, requiring
        # them to download the logs and find the error this way the tests should error as they won't be able
        # to lookup AWS resources on the name (with "MISSING_OUTPUT_" prefix)
        msg = f"Missing terraform output: {resource}"
        print(msg)
        Messages.write_message(msg)
        return f"MISSING_OUTPUT_{resource}"
