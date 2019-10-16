from datetime import timedelta

from django.utils.translation import ugettext_lazy as _

# Shirts
SHIRT_SIZE_CHOICES = [
    ("S", "S"),
    ("M", "M"),
    ("L", "L"),
    ("XL", "XL"),
    ("XXL", "XXL"),
    ("XXXL", "XXXL"),
]

SHIRT_TYPES_CHOICES = [
    ("m", _("classic")),
    ("f", _("female")),
]

# Admin commands
ADMIN_USER_PREFERENCES_COMMAND_TOGGLE_PAYMENT = "toggle_payment_accepted"

ADMIN_USER_PREFERENCES_COMMAND_CHANGE_BONUS = "change_bonus"


# Rooming
class RoomingStatus:
    ROOMING_UNAVAILABLE = 0
    BEFORE_ROOMING = 1
    AFTER_ROOMING = 2
    ROOMING_PROGRESS = 3


MIN_BONUS_MINUTES = 0

MAX_BONUS_MINUTES = 600

ROOM_LOCK_TIMEOUT = timedelta(hours=3)

# Lectures
DURATION_CHOICES = [
    ("10", "10"),
    ("15", "15"),
    ("20", "20"),
    ("30", "30"),
    ("45", "45"),
    ("60", "60"),
    ("75", "75"),
    ("90", "90"),
    ("120", "120")
]

LECTURE_TYPE = [
    ("0", _("Lecture")),
    ("1", _("Workshop"))
]

PERSON_TYPE = [
    ("0", _("Sponsor")),
    ("1", _("Guest")),
    ("2", _("Normal"))
]
