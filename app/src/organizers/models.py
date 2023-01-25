import re

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from users.models import User
from conferences.models import Zosia

def validate_phone_number(value):
    phone_reg = r'\d{9}'
    m = re.match(phone_reg, value)
    if not m:
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
        max_length=9,
        validators=[validate_phone_number]
    )
    zosia = models.ForeignKey(
        Zosia,
        on_delete=models.CASCADE,
        verbose_name=_('ZOSIA')
    )