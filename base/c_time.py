import calendar
import datetime
import platform
import time

from base.c_resource import CResource


class CTime:
    @classmethod
    def now(cls):
        return datetime.datetime.now()

    @classmethod
    def yesterday(cls):
        return datetime.timedelta(days=1)

    @classmethod
    def today(cls):
        return datetime.datetime.today()

    @classmethod
    def from_datetime_str(cls, date_time_str: str, default_date: datetime, datetime_format: str = '%Y-%m-%d %H:%M:%S'):
        try:
            return datetime.datetime.strptime(date_time_str, datetime_format)
        except:
            return default_date

    @classmethod
    def from_date_str(cls, date_time_str: str, default_date: datetime, datetime_format: str = '%Y-%m-%d %H:%M:%S'):
        try:
            return datetime.datetime.date(date_time_str, datetime_format)
        except:
            return default_date

    @classmethod
    def format_str(cls, date_time_value: datetime, datetime_format: str = '%Y-%m-%d %H:%M:%S'):
        return date_time_value.strftime(datetime_format)

    @classmethod
    def year(cls, me: datetime = None):
        if me is None:
            return cls.today().year
        else:
            return me.year

    @classmethod
    def month(cls, me: datetime = None):
        if me is None:
            return cls.today().month
        else:
            return me.month

    @classmethod
    def day(cls, me: datetime = None):
        if me is None:
            return cls.today().day
        else:
            return me.day

    @classmethod
    def yearweek(cls, me: datetime = None):
        if me is None:
            return cls.today().isocalendar()[1]
        else:
            return me.isocalendar()[1]

    @classmethod
    def weekday(cls, me: datetime = None):
        if me is None:
            result = cls.today().weekday() + 1
        else:
            result = me.weekday() + 1

        if result == 7:
            return 0
        else:
            return result

    @classmethod
    def give_me_date(cls, year, month, day):
        return datetime.date(year, month, day)

    @classmethod
    def give_me_time(cls, year, month, day, hour, minute, second, microsecond=0):
        return datetime.datetime(
            year, month=month, day=day, hour=hour, minute=minute, second=second,
            microsecond=microsecond
        )

    @classmethod
    def day_after_day(cls, me: datetime):
        return me + datetime.timedelta(days=1)

    @classmethod
    def month_day_count_of_date(cls, me: datetime):
        week_num, days_count = calendar.monthrange(me.year, me.month)
        return days_count

    @classmethod
    def second_between(cls, time1: datetime, time2: datetime):
        if time2 > time1:
            return (time2 - time1).seconds
        else:
            return (time1 - time2).seconds

    @classmethod
    def sleep(cls, second):
        time.sleep(second)

    @classmethod
    def first_month_day_of_date(cls, date_value: datetime):
        return date_value.replace(day=1)

    @classmethod
    def last_month_day_of_date(cls, date_value: datetime):
        return date_value.replace(day=calendar.monthrange(date_value.year, date_value.month)[1])

    @classmethod
    def first_year_day_of_date(cls, date_value: datetime):
        return date_value.replace(month=1, day=1)

    @classmethod
    def last_year_day_of_date(cls, date_value: datetime):
        return date_value.replace(month=12, day=31)

    @classmethod
    def time(cls):
        if platform.system() == CResource.OS_Windows:
            return time.clock()
        else:
            return time.time()

    @classmethod
    def time_between(cls, time1, time2):
        return time2 - time1
