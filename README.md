# zosia16-site
Django 1.10 version of ZOSIA registration page - v2016 edition.

## Development

### Localhost approach
#### Static components (bower)
* Ensure you have `npm` installed
* Install dependencies with: `npm i`
* Install bower components with `make deps`

#### Google APIs
Google API key is needed for map display. Set it in settings as `GAPI_KEY`.

#### Mailgun
Mailgun API key is needed for sending mails. For development, simply use Console backend, or set up your own mailgun account.

#### Virtualenv
Create virtualenv for python 3.5.
* `virtualenv env`
* `source env/bin/activate`
* `pip install -r requirements`

#### Dev settings
Keep dev settings in `zosia16/settings/dev`. Add setting DJANGO_SETTINGS_MODULE to virtualenv:
* `cat .env.sh >> env/bin/activate`
```
echo '
from .common import *

DEBUG = True
' > zosia16/settings/dev.py
```

#### Spin up db
Use docker:
* `bash tools/run_postgres.sh`
* Wait for container to setup up db..
* `bash tools/setup_db.sh`
Connect to db by setting '127.0.0.1' host in dev settings:
* `echo 'DATABASES['default']['HOST'] = '127.0.0.1'' >> zosia16/settings/dev.py`

### Full in-docker development (if you are on Windows)
#### Setup settings/dev.py
Use `dev.examaple.py` and add:
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'db',
        'PORT': 5432,
    }
}

ALLOWED_HOSTS = ['*']
```
#### Build and run docker containers:
`docker-compose up --build -d`
#### Setup node modules
`docker exec -it zosia16site_web_1 ln -s ../node_modules ./`
#### Run migrations
`docker exec -it zosia16site_web_1 python manage.py migrate`
#### Pull frontend deps
`docker exec -it zosia16site_web_1 make deps`
