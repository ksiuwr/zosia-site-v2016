# -*- coding: utf-8 -*-
import os

from django import template

register = template.Library()


@register.filter
def basename(filepath):
    return os.path.basename(filepath)
