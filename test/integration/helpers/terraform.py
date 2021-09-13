import json
import os

OUTPUTS_FILE = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "terraform_outputs_list-reconciliation.json"
)


def get_terraform_output(resource):
    try:
        outputs = {k: v["value"] for k, v in json.load(open(OUTPUTS_FILE)).items()}
        return outputs[resource]
    except KeyError:
        print(f"Missing terraform output: {resource}")
        return f"MISSING_OUTPUT_{resource}"
