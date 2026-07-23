#!/bin/sh
set -e

# Only wait for Postgres if we're actually using it (not sqlite)
if [ "$DB_ENGINE" = "postgres" ]; then
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