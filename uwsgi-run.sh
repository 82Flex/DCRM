#!/bin/bash

if [ "${DCRM_WORKER}" = "none" ]; then
    sleep 15  # wait for db to be ready
    python manage.py collectstatic --no-input
    python manage.py migrate --no-input
    uwsgi --ini uwsgi.ini
elif [ "${DCRM_WORKER}" = "default" ]; then
    sleep 30  # wait for main app to launch
    python manage.py rqworker default
elif [ "${DCRM_WORKER}" = "high" ]; then
    sleep 30  # wait for main app to launch
    python manage.py rqworker high
elif [ "${DCRM_WORKER}" = "scheduler" ]; then
    sleep 30  # wait for main app to launch
    python manage.py rqscheduler
fi

