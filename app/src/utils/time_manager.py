# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.utils import timezone
from django.utils.dateparse import parse_datetime


def to_timezone(dt):
    if dt and timezone.is_naive(dt):
        dt = timezone.make_aware(dt)

    return dt


def parse_timezone(time_string):
    return to_timezone(parse_datetime(time_string))


def now_time(utc=True):
    return to_timezone(timezone.now()) if utc \
        else to_timezone(timezone.localtime())


def timedelta_since(time, *, delta=None, days=0, hours=0, minutes=0, seconds=0):
    if not delta:
        delta = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

    return to_timezone(time + delta)


def timedelta_since_now(*, utc=True, delta=None, days=0, hours=0, minutes=0, seconds=0):
    return timedelta_since(now_time(utc=utc), delta=delta, days=days,
                           hours=hours, minutes=minutes, seconds=seconds)


def time_point(year, month, day, hour=0, minute=0, second=0):
    return to_timezone(datetime(year, month, day, hour, minute, second))


def convert_zone(time, zone):
    return timezone.localtime(time, zone)


def set_default_zone():
    timezone.deactivate()


def set_current_zone(zone):
    timezone.activate(zone)


def current_zone_name():
    return timezone.get_current_timezone_name()


def default_zone_name():
    return timezone.get_default_timezone_name()
