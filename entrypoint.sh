#!bin/bash -x

sleep 180
#python manage.py collectstatic --noinput
python manage.py syncdb
python manage.py schemamigration PManager --init
#python manage.py schemamigration PManager --auto
python manage.py migrate PManager
#python manage.py migrate sessions

gunicorn tracker.wsgi:application -b 0.0.0.0:8000 --reload
