#!/bin/sh
set -e

if [ "$DB_ENGINE" = "postgres" ] && [ -n "$DB_HOST" ]; then
  echo "Waiting for Postgres at $DB_HOST:$DB_PORT..."
  while ! nc -z "$DB_HOST" "$DB_PORT"; do
    sleep 0.5
  done
  echo "Postgres is up."
fi

echo "Running migrations..."
python manage.py migrate --noinput

# Auto-create a superuser if one doesn't exist (uses env vars, safe to run every deploy)
if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
  echo "Ensuring superuser exists..."
  python manage.py createsuperuser --noinput || true
fi

echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3