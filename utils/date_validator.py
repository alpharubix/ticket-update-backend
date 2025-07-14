from datetime import datetime
import pytz
def india_to_utc(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    india_dt = pytz.timezone('Asia/Kolkata').localize(dt)
    utc_dt = india_dt.astimezone(pytz.UTC)
    return utc_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def get_date(date_str):
    date_only = date_str.split(' ')[0]
    return date_only
