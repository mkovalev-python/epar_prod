# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from PManager.models.tasks import PM_Tracker, PM_Role
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = "Добавляет начальные данные"

    def handle(self, *args, **kwargs):
        site = Site.objects.create(domain='example.com', name='example.com')
        user = User.objects.create_superuser("admin", "admin@example.com", "admin")
        # tracker = PM_tracker(
        #     name="Tracker", code="Tracker", description="Tracker", admin=user, logo=None
        # )
        # tracker.save()
        # role1 = PM_Role.objects.create(code='manager', name='manager', tracker=tracker)
        # role2 = PM_Role.objects.create(code='guest', name='guest', tracker=tracker)
        # role3 = PM_Role.objects.create(code='employee', name='employee', tracker=tracker)
