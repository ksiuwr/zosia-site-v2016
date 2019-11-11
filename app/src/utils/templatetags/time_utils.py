# -*- coding: utf-8 -*-
from django import template

from utils.constants import DEFAULT_TIME_FORMAT
from utils.time_manager import format_in_zone, now

register = template.Library()


@register.simple_tag
def server_time():
    return now().strftime(DEFAULT_TIME_FORMAT)


@register.filter
def zoneformat(time, zonename):
    return format_in_zone(time, zonename, DEFAULT_TIME_FORMAT)


@register.filter
def isoformat(time):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ")
