import os

from .common import *

DEBUG = False

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# Logs SQL queries. Should be enough, since we can check docker logs
LOGGING = {
    "version": 1,
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        }
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
        },
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "/var/log/django.log",
        },
    },
    "loggers": {
        "django.db.backends": {
            "level": "DEBUG",
            "handlers": ["file", "console"],
        },
        "django": {
            "level": "INFO",
            "handlers": ["file", "console"],
        },
    },
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

DATABASES["default"]["CONN_MAX_AGE"] = 5
DATABASES["default"]["HOST"] = os.environ.get("DB_HOST")
DATABASES["default"]["USER"] = os.environ.get("DB_USERNAME")
DATABASES["default"]["PASSWORD"] = os.environ.get("DB_PASSWORD")

# This, in conjunction with DEBUG=True enables 'debug' directives in templates
# Especially room.js makes heavy use of it
INTERNAL_IPS = ["127.0.0.1"]

# Django REST framework (https://www.django-rest-framework.org)
# Disable BrowsableAPIRenderer for production
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",)
}
