# -*- coding: utf-8 -*-
import re
from django import template

register = template.Library()


@register.filter
def name_only(path):
    m = re.match(r'([^/]*/)*([^\.]*).\w+$', path)
    if m:
        return m.group(2)
    return path
