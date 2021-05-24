__author__ = 'tracker_maker'
from django.core.management.base import NoArgsCommand
from django.conf import settings
from django.contrib.auth.models import User
from PManager.models import PM_User, PM_Project
import datetime
from django.utils import timezone

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        users = User.objects.filter(
            is_staff=True,
            is_active=True,
            id__in=PM_User.objects.filter(
                premium_till__lt=timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())
            ).values_list('user__id', flat=True)
        ).exclude(is_superuser=True)

        aUserIds = list(users.values_list('id', flat=True))
        print aUserIds
        print "\r\n"

        users.update(is_staff=False)

        projects = PM_Project.objects.filter(author__in=aUserIds).exclude(locked=True)
        print projects.values_list('name')
        projects.update(locked=True)
        print "\r\n\r\n"