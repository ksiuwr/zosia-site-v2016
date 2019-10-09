# -*- coding: utf-8 -*-
from django import template

from utils.time_manager import format_in_zone

register = template.Library()


@register.filter
def zoneformat(time, zonename):
    return format_in_zone(time, zonename, "%d.%m.%Y %H:%M %Z")
