import os

from uuid import uuid4

from spine_aws_common.lambda_application import LambdaApplication

from comparison_engine.core import compare_records
from listrec_comparison_engine import listrec_comparisons
from utils.database.models import DemographicsDifferences, Demographics
from utils.logger import success, error, Message

cwd = os.path.dirname(__file__)
ADDITIONAL_LOG_FILE = os.path.join(cwd, "..", "..", "utils/cloudlogbase.cfg")


class DemographicComparison(LambdaApplication):
    def __init__(self):
        super().__init__(additional_log_config=ADDITIONAL_LOG_FILE)
        self.job_id = None
        self.patient_id = None

    def initialise(self):
        pass

    def start(self):
        try:
            self.job_id = str(self.event["job_id"])
            self.patient_id = str(self.event["patient_id"])

            self.log_object.set_internal_id(self.job_id)

            self.response = self.demographic_comparisons()

        except KeyError as err:
            self.response = error(
                f"LR08 Lambda tried to access missing key={str(err)}", self.log_object.internal_id
            )

        except Exception:
            self.response = error(
                f"Unhandled exception caught in LR08 Lambda", self.log_object.internal_id
            )

    def demographic_comparisons(self) -> Message:
        """Compare PDS and GP demographic data for a record, logging the result to
        DynamoDB.

        Returns:
            Message: A result containing a status and message
        """

        record = Demographics.get(self.patient_id, self.job_id)

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

        if gp_record["GP_GpPracticeCode"] != pds_record["PDS_GpPracticeCode"]:
            self.log_object.write_log(
                "LR08I04",
                log_row_dict={
                    "patient_id": self.patient_id,
                    "job_id": self.job_id,
                },
            )
            record.update(actions=[Demographics.IsComparisonCompleted.set(True)])

            return success(
                f'LR08 Lambda application stopped for jobId="{self.job_id}"',
                self.log_object.internal_id,
            )

        results = compare_records(listrec_comparisons, gp_record, pds_record)

        self.log_object.write_log(
            "LR08I01",
            log_row_dict={
                "differences_count": len(results),
                "patient_id": self.patient_id,
                "job_id": self.job_id,
            },
        )

        with DemographicsDifferences.batch_write() as batch:
            items = [
                DemographicsDifferences(
                    str(uuid4()), JobId=self.job_id, PatientId=self.patient_id, RuleId=result
                )
                for result in results
            ]

            for item in items:
                batch.save(item)

        self.log_object.write_log(
            "LR08I02", log_row_dict={"patient_id": self.patient_id, "job_id": self.job_id}
        )

        record.update(actions=[Demographics.IsComparisonCompleted.set(True)])

        self.log_object.write_log(
            "LR08I03", log_row_dict={"patient_id": self.patient_id, "job_id": self.job_id}
        )

        return success(
            f"LR08 Lambda application stopped for jobId='{self.job_id}'",
            self.log_object.internal_id,
        )
