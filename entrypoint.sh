#!/bin/sh
set -e

# Only wait for Postgres via host/port if DB_HOST is actually set
# (local docker-compose setup). On Render, DATABASE_URL is used instead,
# and Render only starts this container once the DB is reachable, so no wait is needed.
if [ "$DB_ENGINE" = "postgres" ] && [ -n "$DB_HOST" ]; then
  echo "Waiting for Postgres at $DB_HOST:$DB_PORT..."
  while ! nc -z "$DB_HOST" "$DB_PORT"; do
    sleep 0.5
  done
  echo "Postgres is up."
fi

echo "Running migrations..."
python manage.py migrate --noinput

echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3