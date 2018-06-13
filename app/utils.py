import calendar
from datetime import datetime

import json

from validate_email import validate_email
from urllib.request import urlopen


def year_month_min_date(date: datetime):
    dt = date.date()
    min_dt = datetime(dt.year, dt.month, 1, 00, 00, 0)
    return min_dt


def year_month_max_date(date: datetime):
    dt = date.date()
    last_day = calendar.monthrange(dt.year, dt.month)[1]
    max_dt = datetime(dt.year, dt.month, last_day, 23, 59, 59)
    return max_dt


def year_month_date(date: datetime):
    return year_month_min_date(date), year_month_max_date(date)


def is_valid_email(email: str, check_mx: bool) -> bool:
    dns_valid = validate_email(email, check_mx=check_mx)
    if not dns_valid:
        return False

    validate_url = 'https://open.kickbox.com/v1/disposable/{0}' + email
    response = urlopen(validate_url)
    if response.status != 200:
        return False

    data = response.read()
    json_object = json.loads(data.decode("utf-8"))
    is_disposable = json_object['disposable']
    return not is_disposable


def stable_date(date: datetime):
    return date.replace(microsecond=0)
