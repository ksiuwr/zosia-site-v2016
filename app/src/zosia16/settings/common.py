"""
Django settings for zosia16 project.

Generated by 'django-admin startproject' using Django 1.10.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
import random
import string

import raven

# Google API key
GAPI_KEY = os.environ.get('GAPI_KEY')


# SECURITY WARNING: keep the secret key used in production secret!
def random_string(length=10):
    return ''.join(
        random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(length))


SECRET_KEY = os.environ.get('SECRET_KEY', random_string(20))

if "SECRET_KEY" not in os.environ:
    os.environ['SECRET_KEY'] = SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = os.environ.get('HOSTS', 'staging.zosia.org').split(',')

AUTH_USER_MODEL = "users.User"

# Mailgun (https://github.com/anymail/django-anymail)
ANYMAIL = {
    "MAILGUN_API_KEY": os.environ.get('MAILGUN_API_KEY'),
    # TODO: this shouldn't be hardcoded
    "MAILGUN_SENDER_DOMAIN": 'mail.zosia.org',
}
EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
DEFAULT_FROM_EMAIL = "admin@" + ANYMAIL["MAILGUN_SENDER_DOMAIN"]

# Sentry (https://getsentry.io)
# FIXME this variable (`sentry_dsn`) isn't set anywhere and raven isn't
# integrated in any place anyway, so if you feel like it it would be
# really cool if you added the support
sentry_dsn = os.environ.get('SENTRY_DSN')
if sentry_dsn:
    RAVEN_CONFIG = {
        'dsn': sentry_dsn,
        # If you are using git, you can also automatically configure the
        # release based on the git info.
        'release': raven.fetch_git_sha(os.path.dirname(os.pardir)),
    }

# Django REST framework (https://www.django-rest-framework.org)
REST_FRAMEWORK = {
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Application definition

INSTALLED_APPS = [
    'materializecssform',
    'anymail',
    'rest_framework',
    'drf_yasg',
    'raven.contrib.django.raven_compat',
    'rooms.apps.RoomsConfig',
    'blog.apps.BlogConfig',
    'conferences.apps.ConferencesConfig',
    'users.apps.UsersConfig',
    'sponsors.apps.SponsorsConfig',
    'lectures.apps.LecturesConfig',
    'questions.apps.QuestionsConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'zosia16.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, '..', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'zosia16.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'zosia',
        'USER': 'zosia',
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# List of hashing algorithm classes
# https://docs.djangoproject.com/en/2.2/topics/auth/passwords/
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = False

USE_TZ = True

DATE_FORMAT = 'd.n.o'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/static'
