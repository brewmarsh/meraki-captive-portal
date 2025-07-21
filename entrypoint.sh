#!/bin/sh
set -e
flask db upgrade
exec gunicorn --bind 0.0.0.0:$PORT --timeout 120 run:app
