# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from PManager.models.tasks import PM_Tracker, PM_Role
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Добавляет начальные данные"

    def handle(self, *args, **kwargs):
        user = User.objects.create_superuser("admin", "admin@example.com", "admin")
        tracker = PM_tracker.objects.create(
            name="Tracker", code="Tracker", description="Tracker", admin=user, logo=None
        )
        role1 = PM_roles.objects.create(code='manager', name='manager', tracker=tracker)
        role2 = PM_roles.objects.create(code='guest', name='guest', tracker=tracker)
        role3 = PM_roles.objects.create(code='employee', name='employee', tracker=tracker)
