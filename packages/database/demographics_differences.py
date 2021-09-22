import os

from pynamodb.attributes import UnicodeAttribute
from pynamodb.indexes import AllProjection, GlobalSecondaryIndex
from pynamodb.models import Model

AWS_REGION = os.getenv("AWS_REGION")
DEMOGRAPHICS_DIFFERENCES_TABLE = os.getenv("DEMOGRAPHICS_DIFFERENCES_TABLE")


class DemographicsDifferencesJobIdIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "JobId"
        projection = AllProjection()
        read_capacity_units = 1000
        write_capacity_units = 1000

    JobId = UnicodeAttribute(hash_key=True)


class DemographicsDifferences(Model):
    class Meta:
        table_name = DEMOGRAPHICS_DIFFERENCES_TABLE
        region = AWS_REGION
        read_capacity_units = 1000
        write_capacity_units = 1000

    JobIdIndex = DemographicsDifferencesJobIdIndex()

    Id = UnicodeAttribute(hash_key=True)
    JobId = UnicodeAttribute()
    PatientId = UnicodeAttribute()
    RuleId = UnicodeAttribute()
