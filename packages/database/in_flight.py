import os
from datetime import datetime

from pynamodb.attributes import NumberAttribute, UnicodeAttribute, UTCDateTimeAttribute
from pynamodb.models import Model

AWS_REGION = os.getenv("AWS_REGION")
INFLIGHT_TABLE = os.getenv("INFLIGHT_TABLE")


class InFlight(Model):
    class Meta:
        table_name = INFLIGHT_TABLE
        region = AWS_REGION
        read_capacity_units = 1
        write_capacity_units = 1

    JobId = UnicodeAttribute(hash_key=True)
    Timestamp = UTCDateTimeAttribute(default=datetime.now())
    TotalRecords = NumberAttribute()
