# coding=utf-8
__author__ = 'Alwx'
'''
При изменении критичности задачи, проставлении ответственного, создании новой задачи, изменении планового времени
делается проверка, укладывается ли ответственный в свои цели.
Если нет, то выдавается сообщение подтверждения текущей операции.
Если ответственный не укладывается в цели чужих проектов, делать эти операции не разрешается.
'''
from PManager.models.tasks import PM_Task, PM_Milestone
from PManager.classes.datetime.work_time import WorkTime
from django.utils import timezone
import datetime

def check_milestones(initTask):
    result = []
    order = ['-critically', 'dateCreate']
    responsible = initTask.resp
    tasks = PM_Task.objects.filter(resp=responsible, closed=False, virgin=True)
    tasks = tasks.order_by(*order)
    tasks = tasks.values(
        'id',
        'planTime',
        'dateCreate',
        'project__id',
        'milestone__id',
        'resp__id',
        'critically'
    )

    aTasks = []
    aTaskId = []
    now = timezone.make_aware(datetime.datetime.now(), timezone.get_current_timezone())
    step = None
    for task in tasks:
        if step:
            task['dateCreateGantt'] = step
        else:
            task['dateCreateGantt'] = now

        if task['planTime']:
            taskTimer = WorkTime(
                startDateTime=task['dateCreateGantt'],
                taskHours=task['planTime']
            )
            endTime = step = task['dateCreateGantt'] + datetime.timedelta(hours=taskTimer.taskRealTime)
        else:
            endTime = step = task['dateCreateGantt'] + datetime.timedelta(hours=4)

        task['endTime'] = endTime
        task['resp__id'] = task['resp__id'] if task['resp__id'] else 0

        aTasks.append(task)
        aTaskId.append(task['id'])

    milestones = PM_Milestone.objects.filter(
        closed=False,
        date__gt=datetime.datetime.now(),
        tasks__in=aTaskId
    ).order_by('-date')

    milestones = milestones.values(
        'id',
        'name',
        'date',
        'project__name',
    )

    aMilestones = {}
    for milestone in milestones:
        aMilestones[milestone['id']] = milestone

    if milestones:
        for task in aTasks:
            if task['id'] == initTask.id:
                if task['dateCreateGantt'] > milestones[0]['date']:
                    return []  # Если старт изначальной задачи будет позже уже просроченных майлстоунов

            if task['milestone__id']:
                try:
                    milestone = aMilestones.get(task['milestone__id'], None)
                    if milestone and (milestone not in result):
                        if task['endTime'] > milestone['date']:
                            result.append(milestone)

                except PM_Milestone.DoesNotExist:
                    pass

    return result
