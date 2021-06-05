#!bin/bash -x

sleep 120

python manage.py collectstatic --noinput
python manage.py syncdb
python manage.py schemamigration PManager --init
#python manage.py schemamigration PManager --auto
python manage.py migrate PManager
#python manage.py migrate sessions
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin')" | python manage.py shell
echo "from django.contrib.sites.models import Site; site = Site.objects.create(domain='example.com', name='example.com'); site.save()" | python manage.py shell

gunicorn tracker.wsgi:application -b 0.0.0.0:8000 --reload
