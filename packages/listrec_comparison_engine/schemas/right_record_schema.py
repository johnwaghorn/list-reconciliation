from datetime import datetime

from comparison_engine.schema import DateTimeColumn, RightRecord, StringColumn
from listrec_comparison_engine.utils import strip_ws


class PDSRecord(RightRecord):
    ID = StringColumn("NhsNumber", primary_key=True)
    DATE_OF_BIRTH = DateTimeColumn(
        "PDS_DateOfBirth", format=lambda x: datetime.strptime(str(x), "%Y-%m-%d")
    )
    FORENAMES = StringColumn("PDS_Forenames", format=lambda x: strip_ws(" ".join(x)))
    SURNAME = StringColumn("PDS_Surname", format=strip_ws)
    TITLE = StringColumn("PDS_Titles", format=lambda x: strip_ws(", ".join(x)))
    GENDER = StringColumn("PDS_Gender", format=strip_ws)
    ADDRESS = StringColumn("PDS_Address", format=lambda x: strip_ws(", ".join(x)))
    POSTCODE = StringColumn("PDS_PostCode", format=strip_ws)
