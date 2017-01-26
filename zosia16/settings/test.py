from .common import *

DATABASES['default']['USER'] = 'postgres'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
