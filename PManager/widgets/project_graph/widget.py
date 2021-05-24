# -*- coding:utf-8 -*-
__author__ = 'Gvammer'
from PManager.models import PM_Task, PM_ProjectRoles, PM_Timer, ObjectTags, PM_Milestone, PM_Task_Message, PM_User_Achievement
from django.db.models import Sum, Count
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from PManager.widgets.gantt.widget import widget as gantWidget
from django.views.generic import TemplateView
from yandex_money.forms import PaymentForm
from PManager.viewsExt.tools import TextFilters
from yandex_money.models import Payment as YaPayment
from PManager.widgets.kanban.widget import widget as kanbanWidget

def widget(request, headerValues, ar, qargs):
    def get_bet_type_name(bet_type):
        bet_type_name = ''
        for type, name in aBetTypes:
            if type == bet_type:
                bet_type_name = name
        return bet_type_name

    current_project = headerValues['CURRENT_PROJECT']
    bPay = request.POST.get('pay', False)
    summ = int(request.POST.get('sum', 0) or 0)
    pType = request.POST.get('paymentType', '') or 'ac'

    profile = request.user.get_profile()

    total = profile.account_total or 0
    totalProject = profile.account_total_project(current_project)

    bet = profile.sp_price

    aBetTypes = PM_ProjectRoles.type_choices

    roles = []
    realtime, plantime = 0, 0
    isEmployee = False
    closestMilestone = None
    is_client = False
    plantimeClosed = 0
    aM = []
    nvv = 0

    if current_project:
        # o_roles = PM_ProjectRoles.objects.filter(user=request.user, project=current_project).order_by('role__code')
        # for role in o_roles:
        #     setattr(role, 'bet_type_name', get_bet_type_name(role.payment_type))
        #     if not role.rate:
        #         setattr(role, 'rate', bet)
        #
        #     if role.role.code == 'employee':
        #         isEmployee = True
        #
        #     roles.append(role)

        tasks = PM_Task.objects.filter(project=current_project, closed=False).aggregate(Sum('planTime'))
        tasksClosed = PM_Task.objects.filter(project=current_project, closed=True).aggregate(Sum('planTime'))
        realtime = PM_Timer.objects.filter(task__project=current_project, task__closed=False).aggregate(Sum('seconds'))
        realtime = realtime['seconds__sum'] or 0
        plantime = tasks['planTime__sum'] or 0
        plantimeClosed = tasksClosed['planTime__sum'] or 0

        kanban = kanbanWidget(request, headerValues)
        # if kanban['projects_data']:
        #     currentKanbanProject = kanban['projects_data'][0]
        #     if hasattr(currentKanbanProject, 'current_milestone') and not currentKanbanProject.current_milestone.closed:
        #         closestMilestone = currentKanbanProject.current_milestone


        for ms in [
            {
                'name': 'planTimeMainOrg',
                'title': 'Сетевая организация'
            },
            {
                'name': 'planTimeRegulator',
                'title': 'Регулирующий орган'
            },
            {
                'name': 'planTime',
                'title': 'Экспертная организация'
            }
        ]:
            sum = PM_Task.objects.filter(project=current_project, isParent=False).aggregate(
                Sum(ms['name'])
            )[ms['name'] + '__sum'] if current_project else 0
            sum = sum if sum else 0
            sum = float(round(sum))
            ms.update({
                'sum': sum, 'sum_formatted': TextFilters.numberSpaces(sum)})

            aM.append(ms)
            nvv += ms['sum']

        if closestMilestone:
            if not profile.isManager(current_project) and not profile.isClient(current_project):
                aResp = [request.user.id]
            else:
                aResp = [d['resp__id'] for d in closestMilestone.tasks.values('resp__id').annotate(dcount=Count('resp__id'))]

            gantt = gantWidget(request, headerValues, {
                'resp__in': aResp,
                'virgin': True
            })
            tasksId = closestMilestone.tasks.values_list('id', flat=True)

            if closestMilestone.date is not None:
                for task in gantt['tasks']:
                    if task['id'] in tasksId:
                        if 'endTime' in task and task['endTime'] > closestMilestone.date:
                            setattr(closestMilestone, 'wouldOverdue', True)
                            break

            if closestMilestone.elapsedTimeAllRespsPercent - closestMilestone.closedAndReadyTimeAllRespsPercent > 0:
                setattr(closestMilestone,
                        'timeOverClosedTasks',
                        closestMilestone.elapsedTimeAllRespsPercent - closestMilestone.closedAndReadyTimeAllRespsPercent)

            if closestMilestone.closedAndReadyTimeAllRespsPercent - closestMilestone.closedTaskTimeAllRespsPercent > 0:
                setattr(closestMilestone,
                        'readyOverClosedTasks',
                        closestMilestone.closedAndReadyTimeAllRespsPercent - closestMilestone.closedTaskTimeAllRespsPercent)

            if int(closestMilestone.allTimeAllResps) == closestMilestone.allTimeAllResps:
                setattr(closestMilestone,
                        'allTimeAllResps',
                        int(closestMilestone.allTimeAllResps))

            if int(closestMilestone.taskTimeAllResps) == closestMilestone.taskTimeAllResps:
                setattr(closestMilestone,
                        'taskTimeAllResps',
                        int(closestMilestone.taskTimeAllResps))

            if int(closestMilestone.closedTaskTimeAllResps) == closestMilestone.closedTaskTimeAllResps:
                setattr(closestMilestone,
                        'closedTaskTimeAllResps',
                        int(closestMilestone.closedTaskTimeAllResps))

        is_client = current_project.payer.id == request.user.id if current_project.payer else False

    #END CLOSEST MILESTONE

    taskTagCoefficient = 0
    taskTagPosition = 0
    for obj1 in ObjectTags.objects.raw(
                                'SELECT SUM(`weight`) as weight_sum, `id` from PManager_objecttags WHERE object_id=' + str(
                request.user.id) + ' AND content_type_id=' + str(
            ContentType.objects.get_for_model(User).id) + ''):

        for obj2 in ObjectTags.objects.raw(
                                'SELECT COUNT(v.w) as position, id FROM (SELECT SUM(`weight`) as w, `id`, `object_id` from PManager_objecttags WHERE content_type_id=' + str(
            ContentType.objects.get_for_model(User).id) + ' GROUP BY object_id HAVING w >= ' + str(obj1.weight_sum or 0) + ') as v'):
            taskTagPosition = obj2.position + 1
            break

        taskTagCoefficient += (obj1.weight_sum or 0)
        break

    closedTaskQty = int(PM_Task.getQtyForUser(request.user, current_project, {'closed': True, 'active': True}))
    readyTaskQty = int(PM_Task.getQtyForUser(request.user, current_project, {'closed': False, 'status__code': 'ready'}))
    taskQty = int(PM_Task.getQtyForUser(request.user, current_project, {'active': True}))
    allTaskQty = int(PM_Task.getQtyForUser(request.user, None, {'closed': True, 'active': True}))
    commitsQty = PM_Task_Message.objects.filter(project=current_project).exclude(commit=None).count() if current_project else 0
    allBugsQty = PM_Task_Message.objects.filter(bug=True, checked=False, project=current_project).count() if current_project else 0
    allTodoQty = PM_Task_Message.objects.filter(todo=True, checked=False, project=current_project).count() if current_project else 0
    allMilestoneQty = PM_Milestone.objects.filter(closed=False, project=current_project).count() if current_project else 0

    users = None
    columns = []
    if current_project:
        users = User.objects.filter(id__in=current_project.projectRoles.values_list('user__id', flat=True))
        projectSettings = current_project.getSettings()

        for color_code, color in PM_Task.colors:
            settingColor = 'color_name_' + color_code
            if settingColor in projectSettings and projectSettings[settingColor]:
                sum = 0
                sumReg = 0
                sum_elems = PM_Task.objects\
                    .filter(color=color_code, isParent=False, project=current_project)\
                    .annotate(Sum('planTime'))\
                    .values('planTime')

                sum_elemsRegulator = PM_Task.objects\
                    .filter(color=color_code, isParent=False, project=current_project)\
                    .annotate(Sum('planTimeRegulator')) \
                    .values('planTimeRegulator')

                for k in sum_elems:
                    sum += k['planTime']
                for k in sum_elemsRegulator:
                    sumReg += k['planTimeRegulator']

                p = float(sum - sumReg)

                columns.append({'code': color_code, 'name': projectSettings[settingColor], 'prop': 'color',
                                'price': p, 'price_formatted': TextFilters.numberSpaces(p)})

    usersQty = users.count() if users else 0
    achQty = PM_User_Achievement.objects.filter(project=current_project).count() if current_project else 0


    projectData = {
        'allProjectPrice': totalProject,
        'allPrice': total,
        'categories': aM,
        'closedTasksQty': closedTaskQty,
        'readyOpenTasks': readyTaskQty,
        'readyOpenTasksPercent': round(readyTaskQty * 100 / (taskQty or 1), 2),
        'tasksQty': taskQty,
        'allTaskQty': allTaskQty,
        'allBugsQty': allBugsQty,
        'allTodoQty': allTodoQty,
        'commitsQty': commitsQty,
        'allMilestoneQty': allMilestoneQty,
        'usersQty': usersQty,
        'achQty': achQty,
        'taskClosedPercent': int(round(closedTaskQty * 100 / (taskQty or 1))),
        'bPay': bPay,
        'rating': profile.getRating(current_project),
        'fine': profile.getFine(),
        'rate': bet,
        'isClient': is_client,
        # 'roles': roles,
        'project': current_project,
        'isEmployee': isEmployee,
        'premiumTill': profile.premium_till if request.user.is_staff else '',
        'allOpenRealTime': round(realtime/3600.0, 2),
        'allOpenPlanTime': plantime,
        'allClosedPlanTime': plantimeClosed,
        'taskTagCoefficient': taskTagCoefficient,
        'taskTagPosition': taskTagPosition+100,
        'closestMilestone': closestMilestone,
        'need_passport': not request.user.get_profile().documentNumber,
        'isPro': profile.is_outsource,
        'bNeedTutorial': 1 if not PM_Task.objects.filter(author=request.user).exists() else 0,
        'types': columns,
        'nvv': nvv
    }

    return projectData