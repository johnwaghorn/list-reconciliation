from datetime import datetime

from comparison_engine.schema import DateTimeColumn, LeftRecord, StringColumn
from listrec_comparison_engine.utils import strip_ws


class GPRecord(LeftRecord):
    ID = StringColumn("NhsNumber", primary_key=True)
    DATE_OF_BIRTH = DateTimeColumn(
        "GP_DateOfBirth", format=lambda x: datetime.strptime(str(x), "%Y%m%d")
    )
    FORENAMES = StringColumn("GP_Forenames", format=strip_ws)
    SURNAME = StringColumn("GP_Surname", format=strip_ws)
    TITLE = StringColumn("GP_Title", format=strip_ws)
    GENDER = StringColumn(
        "GP_Gender",
        format=lambda x: {"1": "male", "2": "female", "9": "unknown", "0": "other"}[str(x)],
    )
    ADDRESS = StringColumn(
        [
            "GP_AddressLine1",
            "GP_AddressLine2",
            "GP_AddressLine3",
            "GP_AddressLine4",
            "GP_AddressLine5",
        ],
        format=lambda x: strip_ws(", ".join(filter(None, x))),
    )
    POSTCODE = StringColumn("GP_PostCode", format=strip_ws)
