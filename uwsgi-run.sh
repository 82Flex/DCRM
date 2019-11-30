#!/bin/bash

if [ "${DCRM_WORKER}" = "none" ]; then
    python manage.py collectstatic --no-input
    python manage.py migrate --no-input
    uwsgi --ini uwsgi.ini
elif [ "${DCRM_WORKER}" = "default" ]; then
    sleep 60  # wait for main app to launch
    python manage.py rqworker default
elif [ "${DCRM_WORKER}" = "high" ]; then
    sleep 60  # wait for main app to launch
    python manage.py rqworker high
fi

