# -*- coding: utf-8 -*-
__author__ = 'tracker_maker'
from django.core.management.base import NoArgsCommand
from django.conf import settings
from PManager.models import PM_Task, SlackIntegration, PM_Task_Message

import datetime
from django.utils import timezone


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        for integration in SlackIntegration.objects.all():
            now = datetime.datetime.now()
            dateGt = integration.lastSendDate if integration.lastSendDate else now - datetime.timedelta(days=1)

            for message in PM_Task_Message.objects.filter(
                    project=integration.project,
                    code__in=['STATUS_READY', 'STATUS_REVISION', 'TASK_CREATE' , 'TASK_CLOSE'],
                    dateCreate__gt=dateGt
            ):
                color = '#777777'
                if message.code == 'STATUS_READY':
                    color = 'good'
                elif message.code == 'STATUS_REVISION':
                    color = 'danger'
                elif message.code == 'TASK_CREATE':
                    color = 'warning'

                integration.send({
                    "attachments": [
                        {
                            "fallback": u'<https://tracker.ru' + message.task.url + u'|' + message.task.name + u'> ' + message.text,
                            "pretext": u'<https://tracker.ru' + message.task.url + u'|' + message.task.name + u'> ',
                            "color": color,
                            "fields": [{
                                "title": message.author.last_name + ' ' + message.author.first_name,
                                "value": message.text
                            }]
                        }
                    ]
                })

            integration.lastSendDate = now
            integration.save()
