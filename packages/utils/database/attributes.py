import re
from datetime import datetime

from pynamodb.exceptions import AttributeDeserializationError
from pynamodb.attributes import Attribute
from pynamodb.constants import STRING, DATETIME_FORMAT

from utils.datetimezone import get_datetime_now, localize_date


class GMTDateTimeAttribute(Attribute[datetime]):
    """
    An attribute for storing a GMT Datetime
    This func is heavily duplicated from pynamodb\attributes.py
    """
    attr_type = STRING

    def serialize(self, value):
        """
        Takes a datetime object and returns a string
        """
        if value.tzinfo is None:
            value = localize_date(value)

        if value.tzname() != "BST":
            raise ValueError(f"Datetime string '{value}' with timezone '{value.tzname()}' doesn't use the correct timezone 'BST'")

        fmt = value.strftime(DATETIME_FORMAT)
        return fmt

    def deserialize(self, value):
        """
        Takes a datetime string and returns a datetime object
        """
        return self._fast_parse_utc_date_string(value)

    @staticmethod
    def _fast_parse_utc_date_string(date_string: str) -> datetime:
        # Method to quickly parse strings formatted with '%Y-%m-%dT%H:%M:%S.%f+0000'.
        # This is ~5.8x faster than using strptime and 38x faster than dateutil.parser.parse.
        _int = int  # Hack to prevent global lookups of int, speeds up the function ~10%
        try:
            if (len(date_string) != 31 or date_string[4] != '-' or date_string[7] != '-'
                    or date_string[10] != 'T' or date_string[13] != ':' or date_string[16] != ':'
                    or date_string[19] != '.' or date_string[26] != '+'):
                raise ValueError("Datetime string '{}' does not match format '{}'".format(date_string, DATETIME_FORMAT))
            return localize_date(
                datetime(
                    _int(date_string[0:4]), _int(date_string[5:7]), _int(date_string[8:10]),
                    _int(date_string[11:13]), _int(date_string[14:16]), _int(date_string[17:19]),
                    _int(date_string[20:26])
                ),
                "Europe/London"
            )
        except (TypeError, ValueError):
            raise ValueError("Datetime string '{}' does not match format '{}'".format(date_string, DATETIME_FORMAT))