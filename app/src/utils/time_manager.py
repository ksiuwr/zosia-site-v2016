# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.utils import timezone
from django.utils.dateparse import parse_datetime


class TimeManager:
    @staticmethod
    def now(utc=True):
        return TimeManager.to_timezone(timezone.now()) if utc \
            else TimeManager.to_timezone(timezone.localtime())

    @staticmethod
    def timedelta_from_now(*, utc=True, delta=None, days=0, hours=0, minutes=0, seconds=0):
        if not delta:
            delta = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

        return TimeManager.to_timezone(TimeManager.now(utc) + delta)

    @staticmethod
    def today_time(*, utc=True, hour=0, minute=0, second=0):
        today = TimeManager.now(utc)
        today.replace(hour=hour, minute=minute, second=second)

        return TimeManager.to_timezone(today)

    @staticmethod
    def time_point(year, month, day, hour=0, minute=0, second=0):
        return TimeManager.to_timezone(datetime(year, month, day, hour, minute, second))

    @staticmethod
    def set_current_zone(zone):
        timezone.activate(zone)

    @staticmethod
    def set_default_zone():
        timezone.deactivate()

    @staticmethod
    def to_timezone(dt):
        if dt and timezone.is_naive(dt):
            dt = timezone.make_aware(dt)

        return dt

    @staticmethod
    def parse_timezone(time_string):
        return TimeManager.to_timezone(parse_datetime(time_string))

    @staticmethod
    def default_zone_name():
        return timezone.get_default_timezone_name()

    @staticmethod
    def current_zone_name():
        return timezone.get_current_timezone_name()
