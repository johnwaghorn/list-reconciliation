import os

from pynamodb.attributes import NumberAttribute, UnicodeAttribute
from pynamodb.models import Model

AWS_REGION = os.getenv("AWS_REGION")
JOB_STATS_TABLE = os.getenv("JOB_STATS_TABLE")


class JobStats(Model):
    class Meta:
        table_name = JOB_STATS_TABLE
        region = AWS_REGION
        read_capacity_units = 1
        write_capacity_units = 1

    JobId = UnicodeAttribute(hash_key=True)
    TotalRecords = NumberAttribute(null=True)
    OnlyOnGpRecords = NumberAttribute(null=True)
    OnlyOnPdsRecords = NumberAttribute(null=True)
    PdsUpdatedRecords = NumberAttribute(null=True)
    GpUpdatedRecords = NumberAttribute(null=True)
    HumanValidationRecords = NumberAttribute(null=True)
    PotentialPdsUpdateRecords = NumberAttribute(null=True)
    PotentialGpUpdateRecords = NumberAttribute(null=True)
