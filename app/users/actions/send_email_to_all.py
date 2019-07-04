
from django.template import loader
from django.core.mail import send_mass_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.conf import settings

EMAIL_TEMPLATE_NAME = 'users/generic_email.html'


class SendEmailToAll:
    def __init__(self, users, use_https=False):
        self.users = users
        self.use_https = use_https

    def call(self, subject, text):
        from_email = settings.DEFAULT_FROM_EMAIL
        emails = [(subject, text, from_email, [user.email]) for user in self.users]
        send_mass_mail(emails, fail_silently=False)
