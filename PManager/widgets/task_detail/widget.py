# -*- coding:utf-8 -*-
__author__ = 'Gvammer'
from PManager.models import PM_Task, Agreement, PM_Timer, PM_Task_Message, PM_User_PlanTime, PM_ProjectRoles
import datetime, json
from PManager.viewsExt.tools import TextFilters, taskExtensions
from PManager.widgets.tasklist.widget import widget as taskList
from PManager.viewsExt.tasks import TaskWidgetManager
from PManager.viewsExt.tools import templateTools
from django.db.models import Q
from django.http import Http404
from PManager.services.similar_tasks import similar_solutions

from PManager.services.mind.task_mind_core import TaskMind
from PManager.viewsExt.tools import redisSendTaskUpdate

def widget(request, headerValues, arFilter, q):
    widgetManager = TaskWidgetManager()
    cur_user = request.user
    prof = request.user.get_profile()
    task = None
    if 'id' in request.GET or 'number' in request.GET:
        try:
            if 'id' in request.GET:
                task = PM_Task.objects.filter(id=int(request.GET.get('id')), active=True).get()
            elif 'number' in request.GET and 'project' in request.GET:
                task = PM_Task.objects.filter(
                    number=int(request.GET.get('number')),
                    project=int(request.GET.get('project')),
                    parentTask__isnull=True,
                    active=True
                )[0]
        except (PM_Task.DoesNotExist, ValueError, IndexError):
            task = None

        if not task:
            raise Http404(u'Позиция удалена')

        if not cur_user.get_profile().hasAccess(task, 'view'):
            raise Http404(u'Нет прав для просмотра задачи')

        error = ''
        cid = int(request.GET.get('confirm', 0))
        if cid:
            try:
                message = PM_Task_Message.objects.get(pk=cid, task=task)
                if message.code == 'SET_PLAN_TIME':
                    planTime = PM_User_PlanTime.objects.get(task=task, user=message.author)

                    authorProf = message.author.get_profile()

                    if not authorProf.hasRole(task.project, not_guest=True):
                        authorProf.setRole('employee', task.project)
                        if authorProf.is_outsource:
                            Agreement.objects.get_or_create(
                                payer=task.project.payer,
                                resp=authorProf.user
                            )

                    if not authorProf.isEmployee(task.project):
                        task.resp = prof.user
                    else:
                        task.resp = planTime.user

                    task.planTime = planTime.time
                    task.onPlanning = False
                    task.setStatus('revision')
                    task.save()
                    redisSendTaskUpdate({
                        'status': task.status.code,
                        'onPlanning': task.onPlanning,
                        'planTime': task.planTime,
                        'resp': [{
                            'id': task.resp.id,
                            'name': task.resp.first_name + ' ' + task.resp.last_name
                        }],
                        'viewedOnly': request.user.id,
                    })


                    task.systemMessage(
                        u'подтвердил(а) оценку в ' + str(task.planTime) +
                        u'ч. пользователя ' + planTime.user.first_name +
                        u' ' + planTime.user.last_name,
                        cur_user,
                        'CONFIRM_ESTIMATION'
                    )

                    task.sendTaskEmail('new_task', [planTime.user.email])
                elif message.code == 'TIME_REQUEST':
                    if not message.requested_time_approved:
                        if prof and prof.user.id == message.project.payer.id or prof.isManager(message.project):
                            message.requested_time_approved = True
                            message.requested_time_approve_date = datetime.datetime.now()
                            message.requested_time_approved_by = request.user
                            message.task.planTime += int(message.requested_time or 0)
                            message.task.save()
                            message.save()

                return {'redirect': task.url}
            except PM_Task_Message.DoesNotExist:
                pass
            except PM_User_PlanTime.DoesNotExist:
                pass

        setattr(task, 'text_formatted', TextFilters.getFormattedText(task.text) if task.text else '')
        setattr(task, 'text_formatted_ro', TextFilters.getFormattedText(task.text_ro) if task.text_ro else '')
        setattr(task, 'text_formatted_eo', TextFilters.getFormattedText(task.text_eo) if task.text_eo else '')
        # setattr(task, 'responsibleList', task.responsible.all())
        setattr(task, 'observersList', task.observers.all())
        setattr(task, 'canSetOnPlanning', task.onPlanning or task.canEdit(cur_user))
        setattr(task, 'canSetPlanTime', task.canPMUserSetPlanTime(prof))
        setattr(task, 'canSetCritically', task.canEdit(cur_user))
        setattr(task, 'canEdit', task.canEdit(cur_user))
        setattr(task, 'canRemove', task.canPMUserRemove(prof))
        setattr(task, 'canApprove', cur_user.id == task.author.id or prof.isManager(task.project))
        setattr(task, 'canClose', task.canApprove)
        setattr(task, 'taskPlanTime', task.planTime)

        setattr(task, 'taskResp', [{'id': task.resp.id, 'name': task.resp.first_name + ' ' + task.resp.last_name if task.resp.first_name else task.resp.username} if task.resp else {}])

        allTime = task.getAllTime()
        files = taskExtensions.getFileList(task.files.all())
        files_ro = taskExtensions.getFileList(task.files_ro.all())
        files_eo = taskExtensions.getFileList(task.files_eo.all())

        if task:
            #set task readed
            if not request.user.id in [u.id for u in task.viewedUsers.all()]:
                task.viewedUsers.add(request.user)

            hiddenSubTasksExist = False
            arFilter = {
                'parentTask': task
            }
            subtasks = taskList(request, headerValues, {'filter': arFilter}, [], {})
            subtasks = subtasks['tasks']
            for subtask in subtasks:
                if subtask['closed']:
                    hiddenSubTasksExist = True
                    break

        users = widgetManager.getResponsibleList(request.user, headerValues['CURRENT_PROJECT'])
        dict = task.__dict__

        for field, val in dict.iteritems():
            if isinstance(val, datetime.datetime):
                setattr(task, field, val.strftime('%d.%m.%Y %H:%M'))

        messages = task.messages.order_by('-dateCreate').exclude(code="WARNING")
        # userRoles = PM_ProjectRoles.objects.filter(user=request.user, role__code='manager')
        if not request.user.is_superuser:
            if prof.isEmployee(task.project) or prof.isManager(task.project):
                messages = messages.filter(Q(hidden=False) | Q(userTo=request.user.id) | Q(author=request.user.id))
            else:
                messages = messages.filter(Q(userTo=request.user.id) | Q(author=request.user.id))

        if not prof.isManager(task.project):
            if prof.isClient(task.project):
                messages = messages.filter(hidden_from_clients=False)
            if prof.isEmployee(task.project):
                messages = messages.filter(hidden_from_employee=False)

        lamp, iMesCount = 'no-asked', messages.count()

        if iMesCount > 0 and messages[iMesCount - 1]:
            if messages[iMesCount - 1].author and messages[iMesCount - 1].author.id == cur_user.id:
                lamp = 'asked'

        arTodo = []
        arBugs = []
        for mes in messages:
            if mes.userTo and mes.userTo.id == request.user.id:
                mes.read = True
                mes.save()

            if mes.todo:
                arTodo.append({
                    'id': mes.id,
                    'text': mes.text,
                    'checked': mes.checked
                })

            if mes.bug:
                arBugs.append({
                    'id':mes.id,
                    'text': mes.text,
                    'checked': mes.checked
                })

            ob = {
                'canEdit': mes.canEdit(request.user),
                'canDelete': mes.canDelete(request.user),
                'init': True
            }
            if cur_user.get_profile().isManager(task.project):
                ob.update({
                    'hidden_from_clients': mes.hidden_from_clients,
                    'hidden_from_employee': mes.hidden_from_employee
                })
            setattr(mes, 'json', json.dumps(mes.getJson(ob, request.user)))

        try:
            startedTimer = PM_Timer.objects.get(task=task, dateEnd__isnull=True)
        except PM_Timer.DoesNotExist:
            startedTimer = None

        setattr(task, 'todo', arTodo)
        setattr(task, 'bug', arBugs)
        setattr(task, 'planTime', TextFilters.numberSpaces(float(task.planTime)))
        setattr(task, 'planTimeMainOrg', TextFilters.numberSpaces(float(task.planTimeMainOrg)))
        setattr(task, 'planTimeRegulator', TextFilters.numberSpaces(float(task.planTimeRegulator)))
        templates = templateTools.getMessageTemplates()
        taskTemplate = templateTools.get_task_template()

        # brain = TaskMind()
        return {
            'title': task.name,
            'task': task,
            'startedTimerExist': startedTimer != None,
            'startedTimerUserId': startedTimer.user.id if startedTimer else None,
            'project': task.project,
            'is_employee': cur_user.get_profile().isEmployee(task.project),
            'is_manager': cur_user.get_profile().isManager(task.project),
            'user_roles': cur_user.get_profile().getRoles(task.project),
            'files': files,
            'files_ro': files_ro,
            'files_eo': files_eo,
            'time': allTime,
            'subtasks': subtasks,
            'taskTemplate': taskTemplate,
            'users': users,
            'messages': messages,
            # 'solutions': similar_solutions(task.id),
            'lamp': lamp,
            'hiddenSubTasksExist': hiddenSubTasksExist,
            'templates': templates,
            'error': error
            # 'dataSet': len(arParams),
            # 'similarSet': len(tasksSimilar),
            # 'params': arParams
        }