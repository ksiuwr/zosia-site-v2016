# -*- coding: utf-8 -*-
from datetime import timedelta

from django.utils import timezone
from django.utils.dateparse import parse_datetime


class TimeManager:
    @staticmethod
    def now():
        return TimeManager.to_timezone(timezone.now())

    @staticmethod
    def timedelta_from_now(*, delta=None, days=0, hours=0, minutes=0, seconds=0):
        if not delta:
            delta = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

        return TimeManager.to_timezone(timezone.now() + delta)

    @staticmethod
    def default_timezone():
        return timezone.get_default_timezone_name()

    @staticmethod
    def current_timezone():
        return timezone.get_current_timezone_name()

    @staticmethod
    def to_timezone(dt):
        if dt and timezone.is_naive(dt):
            dt = timezone.make_aware(dt)

        return dt

    @staticmethod
    def parse_timezone(time_string):
        return TimeManager.to_timezone(parse_datetime(time_string))
