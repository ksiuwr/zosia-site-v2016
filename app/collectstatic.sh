#!/bin/sh

{

sleep 30
python manage.py collectstatic --no-input

} &
