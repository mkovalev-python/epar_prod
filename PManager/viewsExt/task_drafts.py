# -*- coding:utf-8 -*-
__author__ = 'Rayleigh'
from PManager.viewsExt.tools import templateTools
import json
from django.http import HttpResponse, Http404
from django.template import loader, RequestContext
from PManager.services.task_list import tasks_to_tuple, task_list_prepare
from PManager.models.tasks import PM_Task
from PManager.models.simple_message import SimpleMessage
from PManager.models.users import PM_User
from django.shortcuts import redirect
from PManager.services.task_drafts import draft_simple_msg_cnt, accept_user, get_draft_by_slug
from PManager.services.invites import executors_available, send_invites, get_evaluations
from PManager.models.taskdraft import TaskDraft
from django.shortcuts import HttpResponseRedirect
from PManager.services.tasks import tasks_quantity_users

import logging
logger = logging.getLogger('task_draft_log')

def taskdraft_detail(request, draft_slug):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/?backurl=/taskdraft/' + draft_slug)
    draft = get_draft_by_slug(draft_slug, request.user)
    if not draft:
        raise Http404
    if request.method == 'GET':
        return __show(request, draft)
    elif request.method == 'POST':
        req_method = request.POST.get('_method', 'POST')
        if req_method == 'DELETE':
            return __delete(request, draft)
        elif req_method == 'PUT':
            return __put(request, draft)
        else:
            raise Http404
    raise Http404


def taskdraft_resend_invites(request, draft_slug):
    LIMIT_USER_INVITES_PER_REQUEST = 6
    draft = get_draft_by_slug(draft_slug, request.user)
    if not draft:
        return HttpResponse(json.dumps({'error': 'Приглашение не найдено'}), content_type="application/json")
    if request.method != "POST":
        return HttpResponse(json.dumps({'error': 'Ошибка метода запроса'}), content_type="application/json")
    if draft.tasks.count() < 1:
        return HttpResponse(json.dumps({'error': 'Нет задач в приглашении'}), content_type="application/json")
    if draft.author.id != request.user.id:
        return HttpResponse(json.dumps({'error': 'У вас нет доступа к этому списку'}), content_type="application/json")

    logger.debug('Send invites requested for draft:' + str(draft.id) + ' by user:' + str(request.user.id))
    user_ids = executors_available(draft)
    user_ids.add(483)
    if not user_ids:
        logger.debug('Executors not available')
        return HttpResponse(json.dumps({'error': 'Не найдено подходящих исполнителей'}),
                            content_type="application/json")
    logger.debug('Executors available: ' + ', '.join(str(x) for x in user_ids))
    try:
        users = PM_User.objects.filter(user_id__in=user_ids)[:LIMIT_USER_INVITES_PER_REQUEST]
        logger.debug('Final users:' + ', '.join(str(x.id) for x in users))
    except (ValueError, PM_User.DoesNotExist):
        logger.debug('Final users not found')
        return HttpResponse(json.dumps({'error': 'Не найдено подходящих исполнителей'}),
                            content_type="application/json")

    send_invites(users, draft)
    arUsers = []
    for profile in users:
        draft.users.add(profile.user)
        profile.setRole('guest', draft.project)
        arUsers.append({
            'id': profile.user.id,
            'full_name': profile.user.first_name + ' ' + profile.user.last_name,
            'avatar': profile.avatarSrc,
            'bet': profile.getBet(draft.project),
            'specialties': [x.name for x in profile.specialties.all()[:4]]
        })

        for task in draft.tasks.all():
            task.observers.add(profile.user)
            task.save()

    draft.status = TaskDraft.OPEN
    draft.save()

    return HttpResponse(json.dumps({'result': 'Найденные исполнители добавлены в задачи.', 'users': arUsers}), content_type="application/json")


def taskdraft_task_discussion(request, draft_slug, task_id):
    draft = get_draft_by_slug(draft_slug, request.user)
    is_xhr = request.GET.get('is_xhr', None)
    if not draft:
        raise Http404
    try:
        task = PM_Task.objects.get(pk=int(task_id))
    except (ValueError, PM_Task.DoesNotExist):
        raise Http404
    if request.method == 'POST':
        return __add_message(request, draft, task)
    evaluations = get_evaluations(request.user, draft, task)
    messages = SimpleMessage.objects.filter(task=task, task_draft=draft).order_by('created_at')
    context = RequestContext(request, {
        'draft': draft,
        'task': task,
        'simple_messages': messages.all(),
        'evaluations': evaluations
    })
    if is_xhr is not None:
        template = loader.get_template('details/taskdraft_task_ajax.html')
    else:
        template = loader.get_template('details/taskdraft_task.html')
    return HttpResponse(template.render(context))


def taskdraft_accept_developer(request, draft_slug, task_id=None):
    draft = get_draft_by_slug(draft_slug, request.user)
    user_accepted_id = request.POST.get('user_id', False)
    if not draft:
        return HttpResponse(json.dumps({'error': 'Список задач не найден'}), content_type="application/json")
    if request.method != "POST":
        return HttpResponse(json.dumps({'error': 'Ошибка метода запроса'}), content_type="application/json")
    if draft.tasks.count() < 1:
        return HttpResponse(json.dumps({'error': 'Нет задач в списке'}), content_type="application/json")
    if draft.author.id != request.user.id:
        return HttpResponse(json.dumps({'error': 'У вас нет доступа к этому списку'}), content_type="application/json")
    if user_accepted_id is False:
        return HttpResponse(json.dumps({'error': 'Неверный Идентификатор пользователя'}),
                            content_type="application/json")
    error = accept_user(draft, task_id, user_accepted_id, request.user)
    if error is False:
        return HttpResponse(json.dumps({'result': 'Пользователь добавлен в проект'}),
                            content_type="application/json")
    return HttpResponse(json.dumps({'error': 'Неудалось подключить пользователя к проекту:\n' + error}),
                        content_type="application/json")

def __add_message(request, draft, task):
    message = request.POST.get('task_message', None)
    if not message:
        return
    message = SimpleMessage.objects.create(text=message.strip(), author=request.user, task=task, task_draft=draft)
    message.save()
    is_xhr = request.GET.get('is_xhr', None)
    if is_xhr is not None:
        context = RequestContext(request, {
            'message': message
        })
        template = loader.get_template('partials/taskdraft_task/taskdraft_task_message.html')
        return HttpResponse(template.render(context))
    else:
        return redirect("/taskdraft/%s/%s" % (draft.slug, task.id))


def __show(request, draft):
    users = draft.users.all()
    (aUsers, allTasksQty) = tasks_quantity_users(users)
    for u in aUsers:
        setattr(u, 'has_role', u.get_profile().hasRole(draft.project))
    tasks = draft.tasks.select_related('resp', 'project', 'milestone', 'parentTask__id', 'author', 'status')\
        .filter(resp__isnull=True)
    add_tasks = dict()
    for task in tasks:
        add_tasks[task.id] = {
            'url': "/taskdraft/%s/%s" % (draft.slug, task.id),
            'project': {
                'name': task.project.name
            },
            'canSetPlanTime': request.user in users,
            'status': task.status.code if task.status else '',
            'last_message': {'text': task.text},
            'messages': draft_simple_msg_cnt(task, draft),
            'resp': [
                {
                    'id': task.resp.id,
                    'name': task.resp.get_full_name()
                } if task.resp else {}
            ]
        }
    tasks = tasks_to_tuple(tasks)
    tasks = task_list_prepare(tasks, add_tasks)

    context = RequestContext(request, {
        'users': aUsers,
        'tasks': tasks,
        'allTasksQty': allTasksQty,
        'draft': draft,
        'tasks_template': templateTools.get_task_template('draft_task')
    })
    template = loader.get_template('details/taskdraft.html')
    return HttpResponse(template.render(context))


def __delete(request, draft):
    if draft.author.id != request.user.id:
        return HttpResponse(json.dumps({'result': 'error'}))
    draft.deleted = True
    draft.save()
    return redirect('/taskdrafts/')


def __put(request, draft):
    if draft.author.id != request.user.id:
        return HttpResponse(json.dumps({'result': 'error'}))
    status_change = request.POST.get('set_status', False)
    if status_change is False:
        return HttpResponse(json.dumps({'result': 'error'}))
    if status_change == 'close':
        draft.status = TaskDraft.CLOSED
        draft.save()
        return redirect('/taskdrafts/')
    elif status_change == 'open':
        draft.status = TaskDraft.OPEN
        draft.save()
        return redirect('/taskdrafts/')
    return HttpResponse(json.dumps({'result': 'error'}))
