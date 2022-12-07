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
    'accommodation_day_1': {'dinner': 'dinner_day_1', 'breakfast': 'breakfast_day_2'},
    'accommodation_day_2': {'dinner': 'dinner_day_2', 'breakfast': 'breakfast_day_3'},
    'accommodation_day_3': {'dinner': 'dinner_day_3', 'breakfast': 'breakfast_day_4'},
}


# Rooming
class RoomingStatus:
    ROOMING_UNAVAILABLE = 0
    BEFORE_ROOMING = 1
    AFTER_ROOMING = 2
    ROOMING_PROGRESS = 3


MIN_BONUS_MINUTES = 0
MAX_BONUS_MINUTES = 600
BONUS_STEP = 3

ROOM_LOCK_TIMEOUT = timedelta(hours=3)


# Lectures
class LectureInternals:
    TYPE_LECTURE = "0"
    TYPE_WORKSHOP = "1"


LECTURE_NORMAL_MAX_DURATION = 60

LECTURE_SPONSOR_MAX_DURATION = 90

WORKSHOP_MIN_DURATION = 30

FULL_DURATION_CHOICES = [
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

LECTURE_NORMAL_DURATION_CHOICES = [d for d in FULL_DURATION_CHOICES if
                                   d[0] <= LECTURE_NORMAL_MAX_DURATION]

LECTURE_SPONSOR_DURATION_CHOICES = [d for d in FULL_DURATION_CHOICES if
                                    d[0] <= LECTURE_SPONSOR_MAX_DURATION]

WORKSHOP_DURATION_CHOICES = [d for d in FULL_DURATION_CHOICES if d[0] >= WORKSHOP_MIN_DURATION]

LECTURE_TYPE = [
    (LectureInternals.TYPE_LECTURE, _("Lecture")),
    (LectureInternals.TYPE_WORKSHOP, _("Workshop"))
]


# Users
class UserInternals:
    PERSON_SPONSOR = "Sponsor"
    PERSON_GUEST = "Guest"
    PERSON_NORMAL = "Normal"
    PERSON_EARLY_REGISTERING = "Early_registering"


PERSON_TYPE = [
    (UserInternals.PERSON_SPONSOR, _("Sponsor")),
    (UserInternals.PERSON_GUEST, _("Guest")),
    (UserInternals.PERSON_NORMAL, _("Normal")),
    (UserInternals.PERSON_EARLY_REGISTERING, _("Early registering"))
]

# Time
DEFAULT_TIME_FORMAT = "%d.%m.%Y %H:%M %Z"

# S3 bucket name
BUCKET_NAME = "zosia-storage"
BUCKET_URL = f"https://{BUCKET_NAME}.s3.eu-central-1.amazonaws.com/"
