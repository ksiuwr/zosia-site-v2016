from .common import *

DEBUG = True
# Set some predefined key to make development easier
# SECRET_KEY = '...'

# Get you Google API key at https://developers.google.com/maps/documentation/embed/guide
# GAPI_KEY = '...'

# Send emails to console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# Or configure mailgun:
# Mailgun (https://github.com/anymail/django-anymail)
# ANYMAIL = {
#     "MAILGUN_API_KEY": '...',,
#     "MAILGUN_SENDER_DOMAIN": '...'
# }


# Logs SQL queries
LOGGING = {
    'version': 1,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        }
    }
}

# No one likes when template is not refreshed after some changes ;)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

DATABASES['default']['HOST'] = 'db'
DATABASES['default']['PASSWORD'] = 'zosia'

# This, in conjunction with DEBUG=True enables 'debug' directives in templates
# Especially room.js makes heavy use of it
INTERNAL_IPS = ['127.0.0.1']
ALLOWED_HOSTS = ['127.0.0.1', '0.0.0.0', 'localhost']

STATICFILES_DIRS = ('/code/static',)
