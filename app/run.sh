#!/bin/sh
set -eu

cd src
python3 ./manage.py migrate
python3 ./manage.py collectstatic --no-input
gunicorn --bind ":$PORT" --workers 2 zosia16.wsgi:application
