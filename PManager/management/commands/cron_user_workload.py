# -*- coding:utf-8 -*-
from django.core.management.base import NoArgsCommand


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        from PManager.models import PMTelegramUser
        for user in PMTelegramUser.objects.filter(telegram_id__isnull=False):
            user.send_workload_request()
