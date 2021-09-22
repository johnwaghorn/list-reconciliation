import os

from pynamodb.attributes import BooleanAttribute, ListAttribute, UnicodeAttribute
from pynamodb.indexes import AllProjection, GlobalSecondaryIndex
from pynamodb.models import Model

AWS_REGION = os.getenv("AWS_REGION")
DEMOGRAPHICS_TABLE = os.getenv("DEMOGRAPHICS_TABLE")


class DemographicsJobIdIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "JobId"
        projection = AllProjection()
        read_capacity_units = 1000
        write_capacity_units = 1000

    JobId = UnicodeAttribute(hash_key=True)


class Demographics(Model):
    class Meta:
        table_name = DEMOGRAPHICS_TABLE
        region = AWS_REGION
        read_capacity_units = 1000
        write_capacity_units = 1000

    JobIdIndex = DemographicsJobIdIndex()

    Id = UnicodeAttribute(hash_key=True)
    JobId = UnicodeAttribute(range_key=True)
    NhsNumber = UnicodeAttribute()
    IsComparisonCompleted = BooleanAttribute(default=False)
    GP_GpPracticeCode = UnicodeAttribute()
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
    PDS_GpPracticeCode = UnicodeAttribute(null=True)
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
