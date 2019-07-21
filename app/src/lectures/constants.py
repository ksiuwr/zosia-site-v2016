from django.utils.translation import ugettext_lazy as _


DURATION_CHOICES = [
    ('5', '5'),
    ('15', '15'),
    ('20', '20'),
    ('25', '25'),
    ('30', '30'),
    ('100', _("Other"))
]


LECTURE_TYPE = [
    ('0', _("Lecture")),
    ('1', _("Workshop"))
]


PERSON_TYPE = [
    ('0', _("Sponsor")),
    ('1', _("Guest")),
    ('2', _("Normal"))
]
