# -*- coding: utf-8 -*-
from django.utils import timezone
from django.utils.dateparse import parse_datetime


class TimeManager:
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
