# -*- coding: utf-8 -*-
__author__ = 'tracker_maker'
from django.core.management.base import NoArgsCommand
from django.conf import settings
from PManager.models import PM_Project, PM_Milestone
from PManager.viewsExt.tools import EmailMessage
import datetime
from django.utils import timezone


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        from datetime import datetime, timedelta, time
        today = datetime.now().date()
        yesterday = today - timedelta(1)
        timeZero = time(0, 0, 0, 0)
        today_start = datetime.combine(today, timeZero)
        yesterday_start = datetime.combine(yesterday, timeZero)
        milestones = PM_Milestone.objects.filter(
            date__lt=today_start,
            date__gte=yesterday_start
        )

        for milestone in milestones:
            users = milestone.project.getUsers()
            for user in users:
                lang = user.get_profile().lang
                if not lang:
                    lang = 'ru'

                arEmail = [user.email]

                if lang == 'ru':
                    sendMes = EmailMessage('feedback_gathering',
                                           {
                                               'client': user,
                                               'project': milestone.project,
                                           },
                                           u'Поделитесь мнением о прошедшем спринте!'
                                           )
                else:
                    sendMes = EmailMessage('feedback_gathering_en',
                                           {
                                               'client': user,
                                               'project': milestone.project,
                                           },
                                           u'Give us a feedback about the finished sprint!'
                                           )

                try:
                    sendMes.send(arEmail)
                    print 'Message has been sent to ' + user.email
                except Exception:
                    print 'Message doesn\'t send'