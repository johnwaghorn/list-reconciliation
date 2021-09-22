import os

from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute
from pynamodb.indexes import AllProjection, GlobalSecondaryIndex
from pynamodb.models import Model

AWS_REGION = os.getenv("AWS_REGION")
JOBS_TABLE = os.getenv("JOBS_TABLE")


class JobsIdIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "JobId"
        projection = AllProjection()
        read_capacity_units = 1000
        write_capacity_units = 1000

    Id = UnicodeAttribute(hash_key=True)


class Jobs(Model):
    class Meta:
        table_name = JOBS_TABLE
        region = AWS_REGION
        read_capacity_units = 1
        write_capacity_units = 1

    IdIndex = JobsIdIndex()

    Id = UnicodeAttribute(hash_key=True)
    PracticeCode = UnicodeAttribute(range_key=True)
    FileName = UnicodeAttribute()
    Timestamp = UTCDateTimeAttribute()
    StatusId = UnicodeAttribute()
