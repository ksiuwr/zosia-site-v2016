# -*- coding: utf-8 -*-
from django import template

from utils.time_manager import convert_zone

register = template.Library()


@register.filter
def zoneformat(time, zonename):
    return convert_zone(time, zonename).strftime("%d.%m.%Y %H:%M %Z")
