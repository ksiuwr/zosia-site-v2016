from django.utils.translation import ugettext as _


SHIRT_SIZE_CHOICES = (
    ('S', 'S'),
    ('M', 'M'),
    ('L', 'L'),
    ('XL', 'XL'),
    ('XXL', 'XXL'),
    ('XXXL', 'XXXL'),
)

SHIRT_TYPES_CHOICES = (
    ('m', _('classic')),
    ('f', _('female')),
)


ADMIN_USER_PREFERENCES_COMMAND_TOGGLE_PAYMENT = 'toggle_payment_accepted'


ADMIN_USER_PREFERENCES_COMMAND_CHANGE_BONUS = 'change_bonus'


GAPI_PLACE_BASE_URL = "https://www.google.com/maps/embed/v1/place"


MIN_BONUS = 0


MAX_BONUS = 250


BONUS_STEP = 5
