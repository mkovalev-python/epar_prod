__author__ = 'tracker_maker'
from django.core.management.base import NoArgsCommand
from django.contrib.auth.admin import User
from PManager.models import PM_Task, PM_Achievement, PM_Project
import datetime
from django.utils import timezone
from PManager.viewsExt.tools import templateTools

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        """
        :param options:
        :return:
        """

        #select count of today closed tasks for users in each project
        users_with_count_of_closed_tasks = PM_Task.objects.raw(
            'SELECT COUNT(*) as cnt, resp_id, project_id, id FROM pmanager_pm_task '
            + 'where closed=1 and dateClose > '
            + '\'' + templateTools.dateTime.convertToDb(datetime.datetime.combine(datetime.datetime.now(), datetime.time.min)) + '\''
            + ' GROUP BY project_id, resp_id'
        )
        achievements = {}
        for i in [5, 10, 15, 20]:
            achievements[i] = PM_Achievement.objects.get(code=(str(i) + '_tasks_closed'))

        projects = {}
        users = {}

        for res in users_with_count_of_closed_tasks:
            if not res.project_id in projects:
                try:
                    projects[res.project_id] = PM_Project.objects.get(pk=res.project_id)
                except PM_Project.DoesNotExist:
                    continue

            if not res.resp_id in users:
                try:
                    users[res.resp_id] = User.objects.get(pk=res.resp_id)
                except PM_Project.DoesNotExist:
                    continue

            for i in achievements:
                if res.cnt < i:
                    continue

                achievements[i].addToUser(users[res.resp_id], projects[res.project_id])