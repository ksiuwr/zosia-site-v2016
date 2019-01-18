
from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

EMAIL_TEMPLATE_NAME = 'users/generic_email.html'

class SendEmailToAll:
    def __init__(self, users, use_https=False):
        self.users = users
        self.use_https = use_https

    def call(self, subject, text):
        to_emails = [user.email for user in self.users]
        email_message = EmailMultiAlternatives(subject, text, None, to_emails)
        email_message.send()

