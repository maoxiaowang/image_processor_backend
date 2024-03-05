#!/bin/bash

if [ "$DB_ENGINE" = "django.db.backends.postgresql" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

#python manage.py collectstatic --noinput

exec "$@"
