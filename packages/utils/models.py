import os

from pynamodb.attributes import (
    UnicodeAttribute,
    UTCDateTimeAttribute,
    NumberAttribute,
    ListAttribute,
    BooleanAttribute,
)
from pynamodb.models import Model
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection

AWS_REGION = os.getenv("AWS_REGION")

DEMOGRAPHICS_TABLE = os.getenv("DEMOGRAPHICS_TABLE")
JOBS_TABLE = os.getenv("JOBS_TABLE")
JOB_STATS_TABLE = os.getenv("JOB_STATS_TABLE")
ERRORS_TABLE = os.getenv("ERRORS_TABLE")
STATUSES_TABLE = os.getenv("STATUSES_TABLE")
DEMOGRAPHICS_DIFFERENCES_TABLE = os.getenv("DEMOGRAPHICS_DIFFERENCES_TABLE")
INFLIGHT_TABLE = os.getenv("INFLIGHT_TABLE")


class DemographicsJobIdIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "demographics-job_id-index"
        projection = AllProjection()
        read_capacity_units = 100
        write_capacity_units = 100

    JobId = UnicodeAttribute(hash_key=True)


class DemographicsDifferencesJobIdIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "demographicsdifferences-job_id-index"
        projection = AllProjection()
        read_capacity_units = 100
        write_capacity_units = 100

    JobId = UnicodeAttribute(hash_key=True)


class JobsIdIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "jobs-id-index"
        projection = AllProjection()
        read_capacity_units = 100
        write_capacity_units = 100

    Id = UnicodeAttribute(hash_key=True)


class DemographicsDifferences(Model):
    class Meta:
        table_name = DEMOGRAPHICS_DIFFERENCES_TABLE
        region = AWS_REGION
        read_capacity_units = 1
        write_capacity_units = 1

    Id = UnicodeAttribute(hash_key=True)
    JobId = UnicodeAttribute()
    PatientId = UnicodeAttribute()
    RuleId = UnicodeAttribute()

    JobIdIndex = DemographicsDifferencesJobIdIndex()


class Demographics(Model):
    class Meta:
        table_name = DEMOGRAPHICS_TABLE
        region = AWS_REGION
        read_capacity_units = 1
        write_capacity_units = 1

    Id = UnicodeAttribute(hash_key=True)
    JobId = UnicodeAttribute(range_key=True)
    NhsNumber = UnicodeAttribute()
    IsComparisonCompleted = BooleanAttribute(default=False)
    GP_GpCode = UnicodeAttribute()
    GP_HaCipher = UnicodeAttribute()
    GP_TransactionDate = UnicodeAttribute()
    GP_TransactionTime = UnicodeAttribute()
    GP_TransactionId = UnicodeAttribute()
    GP_Surname = UnicodeAttribute(null=True)
    GP_Forenames = UnicodeAttribute(null=True)
    GP_PreviousSurname = UnicodeAttribute(null=True)
    GP_Title = UnicodeAttribute(null=True)
    GP_Gender = UnicodeAttribute(null=True)
    GP_DateOfBirth = UnicodeAttribute(null=True)
    GP_AddressLine1 = UnicodeAttribute(null=True)
    GP_AddressLine2 = UnicodeAttribute(null=True)
    GP_AddressLine3 = UnicodeAttribute(null=True)
    GP_AddressLine4 = UnicodeAttribute(null=True)
    GP_AddressLine5 = UnicodeAttribute(null=True)
    GP_PostCode = UnicodeAttribute(null=True)
    GP_DrugsDispensedMarker = BooleanAttribute(null=True)
    GP_RegistrationStatus = UnicodeAttribute(null=True)
    PDS_GpCode = UnicodeAttribute(null=True)
    PDS_GpRegisteredDate = UnicodeAttribute(null=True)
    PDS_Surname = UnicodeAttribute(null=True)
    PDS_Forenames = ListAttribute(null=True)
    PDS_Titles = ListAttribute(null=True)
    PDS_Gender = UnicodeAttribute(null=True)
    PDS_DateOfBirth = UnicodeAttribute(null=True)
    PDS_Sensitive = UnicodeAttribute(null=True)
    PDS_Address = ListAttribute(null=True)
    PDS_PostCode = UnicodeAttribute(null=True)
    PDS_Version = UnicodeAttribute(null=True)

    JobIdIndex = DemographicsJobIdIndex()


class Errors(Model):
    class Meta:
        table_name = ERRORS_TABLE
        region = AWS_REGION
        read_capacity_units = 1
        write_capacity_units = 1

    Id = UnicodeAttribute(hash_key=True)
    JobId = UnicodeAttribute(range_key=True)
    Type = UnicodeAttribute()
    Name = UnicodeAttribute()
    Description = UnicodeAttribute()
    Timestamp = UTCDateTimeAttribute()
    Traceback = UnicodeAttribute()


class Statuses(Model):
    class Meta:
        table_name = STATUSES_TABLE
        region = AWS_REGION
        read_capacity_units = 1
        write_capacity_units = 1

    Id = UnicodeAttribute(hash_key=True)
    Name = UnicodeAttribute()


class Jobs(Model):
    class Meta:
        table_name = JOBS_TABLE
        region = AWS_REGION
        read_capacity_units = 1
        write_capacity_units = 1

    Id = UnicodeAttribute(hash_key=True)
    PracticeCode = UnicodeAttribute(range_key=True)
    FileName = UnicodeAttribute()
    Timestamp = UTCDateTimeAttribute()
    StatusId = UnicodeAttribute()
    IdIndex = JobsIdIndex()


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


class InFlight(Model):
    class Meta:
        table_name = INFLIGHT_TABLE
        region = AWS_REGION
        read_capacity_units = 1
        write_capacity_units = 1

    JobId = UnicodeAttribute(hash_key=True)
    TotalRecords = NumberAttribute()
