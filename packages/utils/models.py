import os

from pynamodb.models import Model
from pynamodb.attributes import ListAttribute, UnicodeAttribute, BooleanAttribute

AWS_REGION = os.getenv("AWS_REGION")


class DemographicsDifferences(Model):
    class Meta:
        table_name = "DemographicsDifferences"
        region = AWS_REGION

    Id = UnicodeAttribute(hash_key=True)
    JobId = UnicodeAttribute()
    PatientId = UnicodeAttribute(null=False)
    RuleId = UnicodeAttribute(null=False)


class Demographics(Model):
    class Meta:
        table_name = "Demographics"
        region = AWS_REGION

    Id = UnicodeAttribute(hash_key=True)
    JobId = UnicodeAttribute(range_key=True)
    NhsNumber = UnicodeAttribute()
    IsComparisonCompleted = BooleanAttribute(default=False)
    GP_GpCode = UnicodeAttribute()
    GP_HaCipher = UnicodeAttribute()
    GP_TransactionDate = UnicodeAttribute()
    GP_TransactionTime = UnicodeAttribute()
    GP_TransactionId = UnicodeAttribute()
    GP_Surname = UnicodeAttribute()
    GP_Forenames = UnicodeAttribute()
    GP_PreviousSurname = UnicodeAttribute(null=True)
    GP_Title = UnicodeAttribute()
    GP_Gender = UnicodeAttribute()
    GP_DateOfBirth = UnicodeAttribute()
    GP_AddressLine1 = UnicodeAttribute()
    GP_AddressLine2 = UnicodeAttribute()
    GP_AddressLine3 = UnicodeAttribute()
    GP_AddressLine4 = UnicodeAttribute()
    GP_AddressLine5 = UnicodeAttribute()
    GP_PostCode = UnicodeAttribute()
    GP_DrugsDispensedMarker = UnicodeAttribute()
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


class Errors(Model):
    class Meta:
        table_name = "Errors"
        region = AWS_REGION

    Id = UnicodeAttribute(hash_key=True)
    JobId = UnicodeAttribute(range_key=True)
    Type = UnicodeAttribute()
    Name = UnicodeAttribute()
    Description = UnicodeAttribute()
    Timestamp = UnicodeAttribute()
    Traceback = UnicodeAttribute()


class Statuses(Model):
    class Meta:
        table_name = "Statuses"
        region = AWS_REGION

    Id = UnicodeAttribute(hash_key=True)
    Name = UnicodeAttribute()


class Jobs(Model):
    class Meta:
        table_name = "Jobs"
        region = AWS_REGION

    Id = UnicodeAttribute(hash_key=True)
    PracticeCode = UnicodeAttribute(range_key=True)
    Filename = UnicodeAttribute()
    Timestamp = UnicodeAttribute()
    StatusId = UnicodeAttribute()
