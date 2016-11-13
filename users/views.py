from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from . import forms
from .models import User


EMAIL_TEMPLATE_NAME = 'users/signup_email.html'
SUBJECT_TEMPLATE_NAME = 'users/signup_email_subject.txt'


# Create your views here.
@login_required
def profile(request):
    return render(request, 'users/profile.html')


def signup(request):
    form = forms.UserForm(request.POST)
    ctx = {
        'form': form,
    }

    if request.method == 'GET' or not form.is_valid():
        return render(request, 'users/signup.html', ctx)

    data = form.cleaned_data

    user = User(
        email=data['email'],
        username=data['username'],
    )
    user.set_password(data['password'])
    user.is_active = False
    user.save()

    current_site = get_current_site(request)
    site_name = current_site.name
    domain = current_site.domain
    context = {
        'domain': domain,
        'site_name': site_name,
        'token': default_token_generator.make_token(user),
        'protocol': 'https',
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'user': user,
    }

    to_email = user.email
    # FIXME: proper email?
    from_email = None
    # NOTE: Copied from django/contrib/auth/forms.py, with adjustments
    subject = loader.render_to_string(SUBJECT_TEMPLATE_NAME, context)
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    body = loader.render_to_string(EMAIL_TEMPLATE_NAME, context)

    email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])

    email_message.send()

    ctx = {
        'email': user.email,
    }

    return render(request, 'users/signup_done.html', ctx)


def activate(request, uidb64, token):
    try:
        # urlsafe_base64_decode() decodes to bytestring on Python 3
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('index')

    ctx = {
        'user': user,
    }
    return render(request, 'users/activate.html', ctx)
