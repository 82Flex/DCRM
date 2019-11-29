#!/bin/bash

python manage.py collectstatic --no-input
python manage.py migrate --no-input
uwsgi --ini uwsgi.ini

