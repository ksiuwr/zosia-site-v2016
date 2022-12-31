
from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.conf import settings


EMAIL_TEMPLATE_NAME = 'users/signup_email.html'
SUBJECT_TEMPLATE_NAME = 'users/signup_email_subject.txt'


class SendActivationEmail:
    def __init__(self, user, site, token_generator, use_https=False):
        self.user = user
        self.site = site
        self.token_generator = token_generator
        self.use_https = use_https

    def call(self):
        site_name = self.site.name
        domain = self.site.domain
        context = {
            'domain': domain,
            'site_name': site_name,
            'token': self.token_generator.make_token(self.user),
            'protocol': 'https' if self.use_https else 'http',
            'uid': urlsafe_base64_encode(force_bytes(self.user.pk)),
            'user': self.user,
        }

        to_email = self.user.email
        # NOTE: Copied from django/contrib/auth/forms.py, with adjustments
        subject = loader.render_to_string(SUBJECT_TEMPLATE_NAME, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(EMAIL_TEMPLATE_NAME, context)

        email_message = EmailMultiAlternatives(
            subject, body, settings.DEFAULT_MAIL, to=[to_email])

        email_message.send()
