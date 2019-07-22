#!/bin/sh

# it's a dirty hack, but it has to suffice for now
python ./manage.py migrate

uwsgi --ini uwsgi.ini
