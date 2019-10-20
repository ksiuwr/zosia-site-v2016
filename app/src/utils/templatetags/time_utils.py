# -*- coding: utf-8 -*-
from django import template

from utils.time_manager import format_in_zone, now

register = template.Library()


@register.simple_tag
def server_time():
    return now().strftime("%d.%m.%Y %H:%M %Z")


@register.filter
def zoneformat(time, zonename):
    return format_in_zone(time, zonename, "%d.%m.%Y %H:%M %Z")
