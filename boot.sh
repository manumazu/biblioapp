#!/bin/sh
. venv/bin/activate
exec gunicorn --bind :5000 --workers 4 --access-logfile - biblioapp:app