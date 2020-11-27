#!/bin/sh
. venv/bin/activate
exec gunicorn --bind :5000 --workers 3 --access-logfile - --error-logfile - biblioapp:app