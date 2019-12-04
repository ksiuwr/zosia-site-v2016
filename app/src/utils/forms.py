# -*- coding: utf-8 -*-
from django.utils.html import escape

from django.utils.safestring import mark_safe


def errors_format(form):
    infos = ["<span><strong>" + escape(field) + "</strong><br/>" + "<br/>".join(map(escape, errs))
             + "</span>" for field, errs in form.errors.items()]

    return mark_safe("<p>" + "<br/><br/>".join(infos) + "</p>")
