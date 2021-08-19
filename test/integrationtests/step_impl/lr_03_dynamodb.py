from getgauge.python import step, Messages, data_store
from .tf_aws_resources import get_terraform_output
import boto3

REGION_NAME = "eu-west-2"
JOBS_TABLE = get_terraform_output("jobs_table")
INFLIGHT_TABLE = get_terraform_output("in_flight_table")
DEMOGRAPHIC_TABLE = get_terraform_output("demographic_table")
DEMOGRAPHIC_DIFFERENCE_TABLE = get_terraform_output("demographics_difference_table")

dev1 = boto3.resource("dynamodb", REGION_NAME)


@step("connect to lr-03 dynamodb and get the latest JobId for a gppractice file")
def get_latest_jobid():
    job_table = dev1.Table(JOBS_TABLE)
    job_data = job_table.scan()
    job_items = []
    for key, value in job_data.items():
        if key == "Items":
            job_items = [j for j in value]
            job_items = sorted(job_items, reverse=True, key=lambda i: i["Timestamp"])
            if job_items:
                latest_job_id = job_items[0]
                return latest_job_id["Id"]


@step("get InFlight table item count")
def get_inflight_table_itemcount():
    inflight_table = dev1.Table(INFLIGHT_TABLE)
    inflight_data = inflight_table.scan()
    print(inflight_data)
    for key, value in inflight_data.items():
        if key == "Count" and value == 0:
            Messages.write_message("inflight table count is :" + str(value))


@step(
    "check expected sensitivity as <exp_pds_sensitive> on demographics table for nhsnumber <exp_nhsnumber>"
)
def check_patient_sensitivity(exp_pds_sensitive, exp_nhsnumber):
    demographic_table = dev1.Table(DEMOGRAPHIC_TABLE)
    demographic_data = demographic_table.scan(ProjectionExpression="NhsNumber, PDS_Sensitive, Id")
    data_store.scenario["demographic_data"] = demographic_data
    sensitive_found = [
        Item
        for Item in demographic_data["Items"]
        if Item["NhsNumber"] == exp_nhsnumber and Item["PDS_Sensitive"] == exp_pds_sensitive
    ]
    assert (
        len(sensitive_found) > 0
    ), f"expected  patient {exp_nhsnumber} not found or expected sensitivity for the patient not found"


@step(
    "check demographic difference <expectedruleid> on demographics difference table for nhsnumber <exp_nhsnumber>"
)
def check_patient_demographic_difference_ruleid(expectedruleid, exp_nhsnumber):
    demographic_data = data_store.scenario["demographic_data"]
    for item in demographic_data["Items"]:
        if item["NhsNumber"] == exp_nhsnumber:
            expected_record = item

    expected_patientid = expected_record["Id"]
    demographic_difference_table = dev1.Table(DEMOGRAPHIC_DIFFERENCE_TABLE)
    demographic_difference_ruleid = demographic_difference_table.scan(
        ProjectionExpression="PatientId, RuleId"
    )
    comparision_found = [
        Item
        for Item in demographic_difference_ruleid["Items"]
        if Item["PatientId"] == expected_patientid and Item["RuleId"] == expectedruleid
    ]
    assert (
        len(comparision_found) > 0
    ), f"expected comparision rule id {expectedruleid} was not applied for {exp_nhsnumber} with patient id {expected_patientid}"
