This is old instruction for local development. **We didn't support it anymore and we highly recommend you to use in-docker developmnet.** But if you realy don't like docker try this approach. You can find old scripts here: https://github.com/ksiuwr/zosia16-site/tree/2900d201c5428297552c584863cd508e1dc93edb/tools

## Development - Localhost approach
### Static components (bower)
* Ensure you have `npm` installed
* Install dependencies with: `npm i`
* Install bower components with `make deps`

### Google APIs
Google API key is needed for map display. Set it in settings as `GAPI_KEY`.

### Mailgun
Mailgun API key is needed for sending mails. For development, simply use Console backend, or set up your own mailgun account.

### Virtualenv
Create virtualenv for python 3.5.
* `virtualenv env`
* `source env/bin/activate`
* `pip install -r requirements`

### Dev settings
Keep dev settings in `zosia16/settings/dev`. Add setting DJANGO_SETTINGS_MODULE to virtualenv:
* `cat .env.sh >> env/bin/activate`
```
echo '
from .common import *

DEBUG = True
' > zosia16/settings/dev.py
```

### Spin up db
Use docker:
* `bash tools/run_postgres.sh`
* Wait for container to setup up db..
* `bash tools/setup_db.sh`
Connect to db by setting '127.0.0.1' host in dev settings:
* `echo 'DATABASES['default']['HOST'] = '127.0.0.1'' >> zosia16/settings/dev.py`