from .common import *

DATABASES['default']['USER'] = 'postgres'
DATABASES['default']['HOST'] = '127.0.0.1'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
