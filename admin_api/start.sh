#!/bin/sh

python manage.py migrate

python manage.py runserver 0.0.0.0:7000 &

python manage.py runrabbitmq
