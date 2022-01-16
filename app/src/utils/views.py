# -*- coding: utf-8 -*-
import csv
from functools import wraps

from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.html import escape
from django.utils.safestring import mark_safe


def anonymous_required(view):
    @wraps(view)
    def func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')

        return view(request, *args, **kwargs)

    return func


def csv_response(header, data, filename='file'):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
    writer = csv.writer(response)
    writer.writerow(header)

    for row in data:
        writer.writerow(row)

    return response


def validation_format(validation_error, info):
    messages = list(map(escape, validation_error.messages))

    return mark_safe(f"<p>{escape(str(info))}:<br/>" + "<br/>".join(messages) + "</p>")
