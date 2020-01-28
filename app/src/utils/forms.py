# -*- coding: utf-8 -*-
from django.utils.html import escape
from django.utils.safestring import mark_safe

from utils.constants import LECTURE_NORMAL_DURATION_CHOICES, LECTURE_SPONSOR_DURATION_CHOICES, \
    LectureInternals, WORKSHOP_DURATION_CHOICES


def errors_format(form):
    infos = ["<span><strong>" + escape(field) + "</strong><br/>" + "<br/>".join(map(escape, errs))
             + "</span>" for field, errs in form.errors.items()]

    return mark_safe("<p>" + "<br/><br/>".join(infos) + "</p>")


def get_durations(lecture_type, person_type):
    if lecture_type == LectureInternals.TYPE_WORKSHOP:
        return WORKSHOP_DURATION_CHOICES

    if lecture_type == LectureInternals.TYPE_LECTURE:
        return LECTURE_SPONSOR_DURATION_CHOICES if person_type == LectureInternals.PERSON_SPONSOR \
            else LECTURE_NORMAL_DURATION_CHOICES

    return []
