from datetime import timedelta

from django.utils.translation import ugettext_lazy as _

DELIMITER = ", "

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

# Conferences
PAYMENT_GROUPS = {
    'accommodation_day_1': ['dinner_day_1', 'breakfast_day_2'],
    'accommodation_day_2': ['dinner_day_2', 'breakfast_day_3'],
    'accommodation_day_3': ['dinner_day_3', 'breakfast_day_4'],
}


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
class LectureInternals:
    TYPE_LECTURE = "0"
    TYPE_WORKSHOP = "1"
    PERSON_SPONSOR = "0"
    PERSON_GUEST = "1"
    PERSON_NORMAL = "2"


DURATION_CHOICES = [
    (10, "10"),
    (15, "15"),
    (20, "20"),
    (30, "30"),
    (45, "45"),
    (60, "60"),
    (75, "75"),
    (90, "90"),
    (120, "120")
]

LECTURE_TYPE = [
    (LectureInternals.TYPE_LECTURE, _("Lecture")),
    (LectureInternals.TYPE_WORKSHOP, _("Workshop"))
]

PERSON_TYPE = [
    (LectureInternals.PERSON_SPONSOR, _("Sponsor")),
    (LectureInternals.PERSON_GUEST, _("Guest")),
    (LectureInternals.PERSON_NORMAL, _("Normal"))
]

# Time
DEFAULT_TIME_FORMAT = "%d.%m.%Y %H:%M %Z"

# S3 bucket name
BUCKET_NAME = "zosia-storage"
BUCKET_URL = f"https://{BUCKET_NAME}.s3.eu-central-1.amazonaws.com/"
