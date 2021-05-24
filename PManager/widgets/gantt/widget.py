# -*- coding:utf-8 -*-
__author__ = 'Gvammer'
from PManager.models import PM_Task, listManager, PM_Milestone, PM_ProjectRoles
from django.contrib.auth.models import User
import datetime
#from django.db.models import Sum,Count
#from PManager.viewsExt.tools import templateTools
#from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db import transaction
from PManager.classes.datetime.work_time import WorkTime
from PManager.models.tasks import PM_Project, PM_MilestoneStatus
from PManager.widgets.tasklist.widget import TaskWidgetManager as widgetManager
from PManager.viewsExt.tools import templateTools


@transaction.commit_manually
def flush_transaction():
    transaction.commit()

def sortGantt(a, b):
    if not a['virgin'] or not b['virgin']:
        return 0
    if a['critically'] == b['critically']:
        return 0
    return -1 if a['critically'] > b['critically'] else 1

def create_milestone_from_post(request, headerValues):
    def pst(n):
        return request.POST.get(n, '')
    try:
        project_id = pst('milestone-project')
        project = PM_Project.objects.get(pk=int(project_id))
    except (PM_Project.DoesNotExist, ValueError) as e:
        project = headerValues['CURRENT_PROJECT']
    if pst('milestone-name') != '' and project:
        name = pst('milestone-name')
        date = pst('milestone-date')
        date = templateTools.dateTime.convertToDateTime(date)
        milestone = PM_Milestone(name=name, date=date, project=project)
        milestone.save()
        return {'redirect': ''}


def widget(request, headerValues, widgetParams={}, qArgs=[]):
    from django.db.models import Q
    bProjectSelected = 'CURRENT_PROJECT' in headerValues

    create_milestone_from_post(request, headerValues)

    def getTaskResponsibleDates(aDates, task, endTime):
        if task['resp__id']:
            if not aDates.get(task['resp__id'], None) or endTime > aDates[task['resp__id']]:
                aDates[task['resp__id']] = endTime
        return aDates

    startHours = 9
    endHour = 18
    holyDays = [5, 6]
    flush_transaction()
    filter = {}
    if isinstance(request, User):
        cur_user = request
    else:
        cur_user = request.user

    user_projects = set(PM_ProjectRoles.objects.filter(user=cur_user).values_list('project_id', flat=True))

    if hasattr(request, 'GET'):
        if request.GET.get('filter', '') == 'Y':
            if request.GET.get('my', '') == 'Y':
                filter['resp'] = cur_user
            if request.GET.get('overdue', '') == 'Y':
                filter['deadline__lte'] = datetime.datetime.now()

    if filter:
        lManager = listManager(PM_Task)
        filter = lManager.parseFilter(filter)

    if 'CURRENT_PROJECT' in headerValues:
        filter['project'] = headerValues['CURRENT_PROJECT']
    else:
        filter['allProjects'] = True

    started_milestones = set(
        PM_MilestoneStatus.objects.filter(
            sprint__closed=False,
            status=PM_MilestoneStatus.STATUS_STARTED
        ).values_list('sprint_id', flat=True)
    )

    milestones = []
    if 'project' in filter:
        milestones = PM_Milestone.objects.filter(project=filter['project'], date__isnull=False)

    if 'filter' in widgetParams:
        filter.update(widgetParams['filter'])

    else:
        qArgs.append(Q(
            Q(realDateStart__isnull=False) | Q(closed=False)
        ))

    # if not 'parentTask' in filter:
    #     filter['parentTask__isnull'] = True
    filter['isParent'] = False
    aManagedProjects = [p.id for p in request.user.get_profile().managedProjects]
    tasks = PM_Task.getForUser(
        request.user,
        filter.get('project', 0),
        filter,
        qArgs,
        {
            'order_by': [
                '-virgin',
                '-realDateStart'
            ]
        }
    )
    tasks = tasks['tasks'].values(
        'id',
        'name',
        'realDateStart',
        'planTime',
        'closed',
        'dateCreate',
        'dateClose',
        'dateModify',
        'milestone__project_id',
        'project__name',
        'status__code',
        'milestone_id',
        'parentTask__name',
        'resp__id',
        'virgin',
        'critically'
    )

    tasks = tasks[:400]

    aTasks = []
    responsibleLastDates = {}
    now = timezone.make_aware(datetime.datetime.now(), timezone.get_current_timezone())
    aResp = []
    aRespProfiles = {}
    for task in tasks:
        if task['resp__id'] and task['resp__id'] not in aResp:
            aResp.append(task['resp__id'])
            aRespProfiles[task['resp__id']] = User.objects.get(pk=task['resp__id']).get_profile()

        task['isMyProject'] = task['milestone__project_id'] in user_projects
        task['isMilestoneStarted'] = task['milestone_id'] in started_milestones
        aTasks.append(task)

    if 'project' in filter and filter['project']:
        if aResp:
            aOtherTasks = []
            otherTasks = PM_Task.objects.filter(resp__in=aResp, closed=False, active=True, project__closed=False).exclude(project=filter['project']).values(
                'id',
                'name',
                'realDateStart',
                'planTime',
                'closed',
                'dateCreate',
                'dateClose',
                'dateModify',
                'project__id',
                'project__name',
                'status__code',
                'milestone_id',
                'milestone__project_id',
                'parentTask__name',
                'author__last_name',
                'author__first_name',
                'resp__id',
                'virgin',
                'critically'
            )
            for task in otherTasks:
                if not task['parentTask__name'] and PM_Task.objects.filter(parentTask__id=task['id'], active=True).count():
                    continue

                task['name'] = task['project__name'] + ': ' + task['name']
                task['parentTask__name'] = ''

                task['otherProject'] = True
                task['isMyProject'] = task['milestone__project_id'] in user_projects
                task['isMilestoneStarted'] = task['milestone_id'] in started_milestones

                aOtherTasks.append(task)

            aTasks = aOtherTasks + aTasks
            aTasks = sorted(aTasks, cmp=sortGantt)

    aTasks = sorted(aTasks, key=lambda k: -k['isMilestoneStarted'])


    #сначала пробежимся по начатым задачам, чтобы выстроить остальные за ними
    aResponsiblesLastDateStart = {}
    for task in aTasks:
        if task['parentTask__name'] and task['name']:
            task['name'] = task['parentTask__name'] + ' / ' + task['name']

        if task['realDateStart']:
            if not task['closed']:
                if task['resp__id'] not in aResponsiblesLastDateStart or \
                                aResponsiblesLastDateStart[task['resp__id']]['realStart'] < task['realDateStart']:
                    aResponsiblesLastDateStart[task['resp__id']] = {
                        'id': task['id'],
                        'realStart': task['realDateStart']
                    }

            if task['planTime']:
                taskTimer = WorkTime(
                    startDateTime=task['realDateStart'],
                    taskHours=task['planTime'],
                    userHoursPerDay=aRespProfiles[task['resp__id']].hoursQtyPerDay if task['resp__id'] in aRespProfiles else 0
                )

                endTime = task['realDateStart'] + datetime.timedelta(hours=taskTimer.taskRealTime)
                if endTime < now and not task['closed']:
                    endTime = now

                responsibleLastDates = getTaskResponsibleDates(responsibleLastDates, task, endTime)

    aTaskMilestones = {}

    for task in aTasks:
        #если время задачи не задано, его надо расчитать
        #if not task['planTime']:
        task['planTime'] = 4 #TODO: продумать, как можно сделать этот параметр динамическим

        if task['resp__id'] in aResponsiblesLastDateStart and \
                        aResponsiblesLastDateStart[task['resp__id']]['id'] == task['id']:
            task['dateCreateGantt'] = task['realDateStart']
        elif task['closed']:
            task['dateCreateGantt'] = task['realDateStart'] if task['realDateStart'] else task['dateCreate']
        else:
            task['dateCreateGantt'] = now
            #если ответственный занят, выстраиваем в ряд
            # for resp in task['responsible']:
            if task['resp__id'] in responsibleLastDates:
                task['dateCreateGantt'] = task['dateCreateGantt'] if task['dateCreateGantt'] > responsibleLastDates[
                    task['resp__id']] else responsibleLastDates[task['resp__id']] + datetime.timedelta(hours=1)

        if task['dateClose']:
            endTime = task['dateClose']
        elif task['planTime']:
            taskTimer = WorkTime(
                startDateTime=task['dateCreateGantt'],
                taskHours=task['planTime'],
                userHoursPerDay=aRespProfiles[task['resp__id']].hoursQtyPerDay if task['resp__id'] in aRespProfiles else 0
            )

            endTime = task['dateCreateGantt'] + datetime.timedelta(hours=taskTimer.taskRealTime)
            if endTime < now and not task['closed']:
                endTime = now
        # elif task['dateModify']:
        #     endTime = now
        # else:
        #     endTime = task['dateCreateGantt'] + datetime.timedelta(hours=1)

        responsibleLastDates = getTaskResponsibleDates(responsibleLastDates, task, endTime)

        task['endTime'] = endTime
        if 'filter' in widgetParams: #ajax call
            task['realDateStart'] = templateTools.dateTime.convertToSite(task['realDateStart'], '%d.%m.%Y %H:%I:%S')
            task['dateCreate'] = templateTools.dateTime.convertToSite(task['dateCreate'], '%d.%m.%Y %H:%I:%S')
            task['dateCreateGantt'] = templateTools.dateTime.convertToSite(task['dateCreateGantt'], '%Y-%m-%dT%H:%I:%S')
            task['endTime'] = templateTools.dateTime.convertToSite(task['endTime'], '%Y-%m-%dT%H:%I:%S')
            task['dateClose'] = templateTools.dateTime.convertToSite(task['dateClose'], '%d.%m.%Y %H:%I:%S')
            task['dateModify'] = templateTools.dateTime.convertToSite(task['dateModify'], '%d.%m.%Y %H:%I:%S')

        if bProjectSelected:
            task['title'] = task['name']
        else:
            task['title'] = task['project__name'] + ': ' + task['name']

        task['full'] = True
        task['resp__id'] = task['resp__id'] if task['resp__id'] else 0

        if task['milestone_id']:
            if task['milestone_id'] not in aTaskMilestones:
                aTaskMilestones[task['milestone_id']] = []

            aTaskMilestones[task['milestone_id']].append(task['id'])

    aMilestones = []
    aDates = []
    for milestone in milestones:
        if milestone.id in aTaskMilestones:
            setattr(milestone, 'tasksId', aTaskMilestones[milestone.id])
        if milestone.date and milestone.date in aDates:
            milestone.date = milestone.date + datetime.timedelta(hours=4)
        if milestone.date:
            aDates.append(milestone.date)
        aMilestones.append(milestone)

    return {
        'title': u'Диаграмма Ганта',
        'tasks': aTasks,
        'milestones': aMilestones,
        'users': widgetManager.getResponsibleList(cur_user, filter['project']),
        'project': filter['project'] if 'project' in filter else False
    }