
import time
import calendar
from datetime import datetime, timedelta


# get 'Asia/Shanghai' local datetime
def dt_now():
    dt = datetime.now()
    delta = timedelta(seconds=time.timezone + 8 * 3600)
    return dt + delta


# get week day of the first day and day numbers of a month
week_day, day_number = calendar.monthrange(2016, 11)

# time stamp to datetime
dt = datetime.fromtimestamp(1488184500000/1e3)

