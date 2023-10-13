# -*- coding: utf-8 -*-
from django.utils.html import escape
from django.utils.safestring import mark_safe

from utils.constants import LECTURE_NORMAL_DURATION_CHOICES, LECTURE_SPONSOR_DURATION_CHOICES, \
    LectureInternals, UserInternals, WORKSHOP_DURATION_CHOICES


def errors_format(form):
    infos = [
        (
            "<span><strong>"
            f"{escape(form.fields[field].label) if field != 'terms_accepted' else 'Terms & Conditions'}"
            "</strong><br/>"
        ) + "<br/>".join(map(escape, errs)) + "</span>" for field, errs in form.errors.items()]

    return mark_safe("<p>" + "<br/><br/>".join(infos) + "</p>")


def get_durations(lecture_type, user):
    if lecture_type == LectureInternals.TYPE_WORKSHOP:
        return WORKSHOP_DURATION_CHOICES

    if lecture_type == LectureInternals.TYPE_LECTURE:
        return LECTURE_SPONSOR_DURATION_CHOICES \
            if user.person_type == UserInternals.PERSON_SPONSOR \
            else LECTURE_NORMAL_DURATION_CHOICES

    return []
