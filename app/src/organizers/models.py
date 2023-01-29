import re

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from conferences.models import Zosia
from users.models import User


def validate_phone_number(value):
    phone_regexes = [
        r'^(\+\d{1,3} ?|\(\+\d{1,3}\) )?\d{9}$',
        r'^(\+\d{1,3} |\(\+\d{1,3}\) )?\d{3} \d{3} \d{3}$',
        r'^(\+\d{1,3}[ -]|\(\+\d{1,3}\) )?\d{3}-\d{3}-\d{3}$'
    ]

    for reg in phone_regexes:
        if re.match(reg, value) is not None:
            break
    else:
        raise ValidationError(_('Please provide correct phone number'))


class OrganizerContact(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('User'),
        limit_choices_to={'is_staff': True}
    )
    phone_number = models.CharField(
        verbose_name=_('Phone number'),
        max_length=20,
        validators=[validate_phone_number]
    )
    zosia = models.ForeignKey(
        Zosia,
        on_delete=models.CASCADE,
        verbose_name=_('ZOSIA')
    )

    def __str__(self):
        return f"Contact to {self.user}"
