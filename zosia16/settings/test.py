from .common import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'zosia',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
