# -*- coding:utf-8 -*-
__author__ = 'Rayleigh'
from PManager.models import PM_Task
import datetime, itertools
from django.utils import timezone

MAX_TASKS_QTY = 10


def tasks_quantity_users(users):
    allUsersTaskQty = 1
    user_list = []
    for user in users:
        tasks_quantity_mixin(user)
        if allUsersTaskQty < user.allTasksQty:
            allUsersTaskQty = user.allTasksQty
        user_list.append(user)
    return (user_list, allUsersTaskQty)


def tasks_quantity_mixin(user):
    profile = user.get_profile()
    allTasksQty = profile.allTasksQty
    taskClosedQty = tasks_closed_by_user(user)
    setattr(user, 'tasksQty', taskClosedQty)
    if allTasksQty > MAX_TASKS_QTY:
        setattr(user, 'overMaxTasks', True)
    setattr(user, 'allTasksQty', allTasksQty)
    setattr(user, 'allTasksQtyForDivision', allTasksQty * 100)


def tasks_closed_by_user(user, startTime=None):
    if startTime is None:
        now = timezone.make_aware(datetime.datetime.now(), timezone.get_current_timezone())
        startTime = now - datetime.timedelta(days=30)
    return PM_Task.objects.filter(
        closed=True,
        resp=user,
        active=True,
        dateClose__gte=startTime).count()
