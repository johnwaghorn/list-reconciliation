from comparison_engine.schema import LeftRecord, StringColumn, DateTimeColumn
from listrec_comparison_engine.format import (
    gp_dob,
    strip_whitespace,
    to_lower,
    gp_gender,
    gp_address,
)


class GPRecord(LeftRecord):
    ID = StringColumn("NhsNumber", primary_key=True)
    DATE_OF_BIRTH = DateTimeColumn("GP_DateOfBirth", formatters=gp_dob)
    FORENAMES = StringColumn("GP_Forenames", formatters=[strip_whitespace, to_lower])
    SURNAME = StringColumn("GP_Surname", formatters=[strip_whitespace, to_lower])
    TITLE = StringColumn("GP_Title", formatters=[strip_whitespace, to_lower])
    GENDER = StringColumn(
        "GP_Gender", formatters=[strip_whitespace, to_lower, gp_gender]
    )
    ADDRESS = StringColumn(
        [
            "GP_AddressLine1",
            "GP_AddressLine2",
            "GP_AddressLine3",
            "GP_AddressLine4",
            "GP_AddressLine5",
        ],
        formatters=[strip_whitespace, to_lower, gp_address],
    )
    POSTCODE = StringColumn("GP_PostCode", formatters=[strip_whitespace, to_lower])
