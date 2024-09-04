from datetime import datetime, timedelta

def get_start_of_today():
    now = datetime.utcnow()
    return datetime(year=now.year, month=now.month, day=now.day)

def get_end_of_today():
    now = datetime.utcnow()
    end_of_today = datetime(year=now.year, month=now.month, day=now.day) + timedelta(days=1) - timedelta(seconds=1)
    return end_of_today

def get_today_date():
    return datetime.utcnow().date()

def get_current_datetime():
    return datetime.utcnow()

def is_same_day(date1: datetime, date2: datetime):
    return date1.date() == date2.date()

def is_greater_than(date1: datetime, date2: datetime):
    return date1 > date2

def convert_to_datetime(date: str):
    return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f")