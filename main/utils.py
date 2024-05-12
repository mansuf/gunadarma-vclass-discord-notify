from datetime import datetime
from zoneinfo import ZoneInfo
from django.utils.dateformat import (
    format as dtformat,
    time_format as tformat
)

def get_datetime():
    tz = ZoneInfo("Asia/Jakarta")
    return datetime.now(tz=tz)

def convert_datetime(dt):
    ot_dt = dtformat(dt, "l, d E Y")
    ot_t = tformat(dt, "H:i:s")

    return f"{ot_dt} {ot_t}"