import re

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from users.models import User
from conferences.models import Zosia

def validate_phone_number(value):
    separators = ['', '-', ' ']
    phone_reg_template = r'^(?:\+\d{{2,3}}{0})?(\d{{3}}{0}){{2}}\d{{3}}$'
    matched = False
    for separator in separators:
        reg = phone_reg_template.format(separator)
        if re.match(reg, value) != None:
            matched = True
            break

    if not matched:
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
        max_length=18,
        validators=[validate_phone_number]
    )
    zosia = models.ForeignKey(
        Zosia,
        on_delete=models.CASCADE,
        verbose_name=_('ZOSIA')
    )