
from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


EMAIL_TEMPLATE_NAME = 'users/signup_email.html'
SUBJECT_TEMPLATE_NAME = 'users/signup_email_subject.txt'


class SendActivationEmail:
    def __init__(self, user, site, token_generator):
        self.user = user
        self.site = site
        self.token_generator = token_generator

    def call(self):
        site_name = self.site.name
        domain = self.site.domain
        context = {
            'domain': domain,
            'site_name': site_name,
            'token': self.token_generator.make_token(self.user),
            'protocol': 'https',
            'uid': urlsafe_base64_encode(force_bytes(self.user.pk)),
            'user': self.user,
        }

        to_email = self.user.email
        # FIXME: proper email?
        from_email = None
        # NOTE: Copied from django/contrib/auth/forms.py, with adjustments
        subject = loader.render_to_string(SUBJECT_TEMPLATE_NAME, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(EMAIL_TEMPLATE_NAME, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])

        email_message.send()
