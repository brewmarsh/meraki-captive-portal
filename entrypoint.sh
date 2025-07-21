#!/bin/sh
set -e
if [ -f .env ]; then
  set -a
  . ./.env
  set +a
fi
flask db upgrade
exec gunicorn --bind 0.0.0.0:$PORT --timeout 120 run:app
