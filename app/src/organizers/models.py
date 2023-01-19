from django.db import models
from django.utils.translation import ugettext_lazy as _

from users.models import User
from conferences.models import Zosia

class OrganizerContact(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        verbose_name=_('User'),
        limit_choices_to={'is_staff': True}
    )
    phone_number = models.CharField(verbose_name=_('Phone number'), max_length=9)
    zosia = models.ForeignKey(
        Zosia,
        on_delete=models.CASCADE,
        verbose_name=_('ZOSIA')
    )