from comparison_engine.schema import DateTimeColumn, RightRecord, StringColumn
from listrec_comparison_engine.format import (
    pds_dob,
    strip_whitespace,
    to_lower,
    pds_address,
)


class PDSRecord(RightRecord):
    ID = StringColumn("NhsNumber", primary_key=True)
    DATE_OF_BIRTH = DateTimeColumn("PDS_DateOfBirth", formatters=pds_dob)
    FORENAMES = StringColumn("PDS_Forenames", formatters=[strip_whitespace, to_lower])
    SURNAME = StringColumn("PDS_Surname", formatters=[strip_whitespace, to_lower])
    TITLE = StringColumn("PDS_Titles", formatters=[strip_whitespace, to_lower])
    GENDER = StringColumn("PDS_Gender", formatters=[strip_whitespace, to_lower])
    ADDRESS = StringColumn("PDS_Address", formatters=[strip_whitespace, to_lower, pds_address])
    POSTCODE = StringColumn("PDS_PostCode", formatters=[strip_whitespace, to_lower])
