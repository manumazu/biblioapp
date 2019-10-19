#!/bin/bash
. venv/bin/activate
export FLASK_APP=biblioapp
export FLASK_ENV=development
flask run
