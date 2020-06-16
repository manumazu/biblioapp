#!/bin/bash
. venv/bin/activate
export FLASK_APP=biblioapp
export FLASK_ENV=development
if [ "$1" != "" ]; then
	flask run --host='192.168.0.29' --cert=bibliobus.cert --key=bibliobus.key
else
	flask run --host='192.168.0.29'
fi	
