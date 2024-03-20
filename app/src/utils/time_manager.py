# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.utils import timezone
from django.utils.dateparse import parse_datetime
import pytz


def to_timezone(dt):
    if dt is not None and timezone.is_naive(dt):
        dt = timezone.make_aware(dt)

    return dt


def parse_timezone(time_string):
    return to_timezone(parse_datetime(time_string))


def now(utc=True):
    return to_timezone(timezone.now() if utc else timezone.localtime())


def timedelta_since(datetime_, *, delta=None, days=0, hours=0, minutes=0, seconds=0):
    if delta is None:
        delta = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

    return to_timezone(datetime_ + delta)


def timedelta_since_now(*, utc=True, delta=None, days=0, hours=0, minutes=0, seconds=0):
    return timedelta_since(now(utc=utc), delta=delta, days=days,
                           hours=hours, minutes=minutes, seconds=seconds)


def time_point(year, month, day, hour=0, minute=0, second=0):
    return to_timezone(datetime(year, month, day, hour, minute, second))


def convert_zone(time, zone_name):
    return timezone.localtime(to_timezone(time), pytz.timezone(zone_name))


def format_in_zone(time, zone_name, format_str):
    return convert_zone(time, zone_name).strftime(format_str)


def set_default_zone():
    timezone.deactivate()


def set_current_zone(zone):
    timezone.activate(zone)


def current_zone_name():
    return timezone.get_current_timezone_name()


def default_zone_name():
    return timezone.get_default_timezone_name()
