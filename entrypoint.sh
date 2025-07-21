#!/bin/sh
set -e
if [ -f .env ]; then
  export $(cat .env | sed 's/#.*//g' | xargs)
fi
flask db upgrade
exec gunicorn --bind 0.0.0.0:$PORT --timeout 120 run:app
