from uuid import uuid4
from typing import Dict

from comparison_engine.core import compare_records
from utils.logger import LOG, success
from listrec_comparison_engine import listrec_comparisons
from utils.models import DemographicsDifferences, Demographics


def demographic_comparisons(job_id: str, patient_id: str) -> Dict[str, str]:
    """Compare PDS and GP demographic data for a record, logging the result to
    DynamoDB.

    Args:
        patient_id (str): Internal ID of the patient to process.
        job_id (str): ID of the job the comparison is being applied under.

    Returns:
        Dict: A result containing a status and message
    """

    record = Demographics.get(patient_id, job_id)

    common_cols = ["Id", "JobId", "NhsNumber"]

    gp_record = {}
    pds_record = {}
    for col, val in record.attribute_values.items():
        if col in common_cols:
            gp_record[col] = val
            pds_record[col] = val

        elif col.startswith("GP_"):
            gp_record[col] = val

        elif col.startswith("PDS_"):
            pds_record[col] = val

    if gp_record["GP_GpCode"] != pds_record["PDS_GpCode"]:
        msg = f"GP Codes for job_id: {job_id} patient_id: {patient_id} do not match (GP: {gp_record['GP_GpCode']}, PDS: {pds_record['PDS_GpCode']})"
        LOG.info(msg)

        return {"status": "success", "message": msg}

    results = compare_records(listrec_comparisons, gp_record, pds_record)

    with DemographicsDifferences.batch_write() as batch:
        items = [
            DemographicsDifferences(str(uuid4()), JobId=job_id, PatientId=patient_id, RuleId=result)
            for result in results
        ]

        for item in items:
            batch.save(item)

    record.update(actions=[Demographics.IsComparisonCompleted.set(True)])

    return success(f"Comparison applied for job_id {job_id} patient_id {patient_id}")
