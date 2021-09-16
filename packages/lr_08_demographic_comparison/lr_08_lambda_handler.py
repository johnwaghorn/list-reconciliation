import traceback
from uuid import uuid4

from comparison_engine.core import compare_records
from database.models import Demographics, DemographicsDifferences
from listrec_comparison_engine import listrec_comparisons
from lr_logging import get_cloudlogbase_config
from lr_logging.responses import Message, error, success
from registration import GPRegistrationStatus
from spine_aws_common.lambda_application import LambdaApplication


class DemographicComparison(LambdaApplication):
    def __init__(self):
        super().__init__(additional_log_config=get_cloudlogbase_config())
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

        except KeyError as e:
            self.response = error(
                f"LR08 Lambda tried to access missing key with error={traceback.format_exc()}",
                self.log_object.internal_id,
            )
            raise e

        except Exception as e:
            self.response = error(
                f"Unhandled exception caught in LR08 Lambda with error={traceback.format_exc()}",
                self.log_object.internal_id,
            )
            raise e

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

        if gp_record["GP_RegistrationStatus"] != GPRegistrationStatus.MATCHED.value:
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
                    str(uuid4()),
                    JobId=self.job_id,
                    PatientId=self.patient_id,
                    RuleId=result,
                )
                for result in results
            ]

            for item in items:
                batch.save(item)

        self.log_object.write_log(
            "LR08I02",
            log_row_dict={"patient_id": self.patient_id, "job_id": self.job_id},
        )

        record.update(actions=[Demographics.IsComparisonCompleted.set(True)])

        self.log_object.write_log(
            "LR08I03",
            log_row_dict={"patient_id": self.patient_id, "job_id": self.job_id},
        )

        return success(
            f"LR08 Lambda application stopped for jobId='{self.job_id}'",
            self.log_object.internal_id,
        )
