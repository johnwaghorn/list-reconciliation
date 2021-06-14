import os

from pynamodb.attributes import (
    ListAttribute,
    UnicodeAttribute,
    BooleanAttribute,
    UTCDateTimeAttribute,
    NumberAttribute,
)
from pynamodb.models import Model
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection

AWS_REGION = os.getenv("AWS_REGION")

DEMOGRAPHICS_TABLE = os.getenv("DEMOGRAPHICS_TABLE")
JOBS_TABLE = os.getenv("JOBS_TABLE")
JOBSTATS_TABLE = os.getenv("JOBSTATS_TABLE")
ERRORS_TABLE = os.getenv("ERRORS_TABLE")
STATUSES_TABLE = os.getenv("STATUSES_TABLE")
DEMOGRAPHICSDIFFERENCES_TABLE = os.getenv("DEMOGRAPHICSDIFFERENCES_TABLE")
INFLIGHT_TABLE = os.getenv("INFLIGHT_TABLE")


class DemographicsDifferences(Model):
    class Meta:
        table_name = DEMOGRAPHICSDIFFERENCES_TABLE
        region = AWS_REGION
        read_capacity_units = 1
        write_capacity_units = 1

    Id = UnicodeAttribute(hash_key=True)
    JobId = UnicodeAttribute()
    PatientId = UnicodeAttribute()
    RuleId = UnicodeAttribute()


class JobIDIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "JobId-index"
        projection = AllProjection()
        read_capacity_units = 1
        write_capacity_units = 1

    JobId = UnicodeAttribute(hash_key=True)


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
    GP_DrugsDispensedMarker = UnicodeAttribute(null=True)
    GP_RegistrationStatus = UnicodeAttribute(null=True)
    PDS_GpCode = UnicodeAttribute(null=True)
    PDS_GpRegisteredDate = UnicodeAttribute(null=True)
    PDS_Surname = UnicodeAttribute(null=True)
    PDS_Forenames = ListAttribute(null=True)
    PDS_Titles = ListAttribute(null=True)
    PDS_Gender = UnicodeAttribute(null=True)
    PDS_DateOfBirth = UnicodeAttribute(null=True)
    PDS_IsSensitive = BooleanAttribute(null=True)
    PDS_Address = ListAttribute(null=True)
    PDS_PostCode = UnicodeAttribute(null=True)

    JobIDIndex = JobIDIndex()


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


class JobStats(Model):
    class Meta:
        table_name = JOBSTATS_TABLE
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
