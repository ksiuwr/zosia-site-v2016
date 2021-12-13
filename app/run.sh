#!/bin/sh
set -eu

python3 ./src/manage.py migrate
gunicorn --bind ":$PORT" --workers 2 zosia16.wsgi:application
