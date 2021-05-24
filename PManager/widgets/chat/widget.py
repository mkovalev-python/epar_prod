# -*- coding:utf-8 -*-
__author__ = 'Gvammer'
from PManager.models import PM_Task_Message, PM_Project
from django.db.models import Q
from django.contrib.auth.models import User
from PManager.viewsExt.tools import templateTools
from tracker import settings


def widget(request, headerValues=None, ar=None, qargs=None):


    last_id = request.REQUEST.get('last_id', 0)
    if request.user.is_superuser:
        hiddenQ = Q(author__isnull=False)
    else:
        hiddenQ = Q(hidden=False)

    managedProjects = request.user.get_profile().getProjects(only_managed=True).values_list('id', flat=True)
    userProjects = request.user.get_profile().getProjects(exclude_guest=True).values_list('id', flat=True)

    unManagedQ = Q(project__in=managedProjects)
    if len(userProjects) != len(managedProjects):
        unManagedQ = unManagedQ | Q(
            Q(
                Q(task__observers=request.user) &
                Q(hidden_from_clients=False) &
                Q(hidden_from_employee=False) |

                Q(task__resp=request.user) |
                Q(task__author=request.user)
                # todo: add hidden from clients and hidden from employee
            ) &
            Q(project__in=userProjects)
        )

    activeProjects = PM_Project.objects.exclude(closed=True, locked=True).values_list('id', flat=True)

    result = PM_Task_Message.objects.filter(
        project__in=activeProjects
    ) \
        .filter(
        Q(author=request.user) |
        Q(userTo=request.user) |
        hiddenQ &
        Q(
            unManagedQ
        )
    ).select_related('author', 'project', 'task', 'task__parentTask', 'modifiedBy')
    # result = result.filter(task__active=True)
    result = result.exclude(code="WARNING")
    chat = request.REQUEST.get('chat', None)
    if chat:
        try:
            chat = User.objects.get(pk=chat)
            result = result.filter(
                Q(author=chat) |
                Q(userTo=chat)
            ).filter(isSystemLog=False)
        except User.DoesNotExist:
            result = result.filter(id=-1)

    options = {
        'MESSAGE_TYPE': 'ALL',
        'OTHER_PROJECTS': False
    }

    if 'FEED_OPTION_MESSAGE_TYPE' in headerValues['COOKIES']:
        options['MESSAGE_TYPE'] = headerValues['COOKIES']['FEED_OPTION_MESSAGE_TYPE'] or 'ALL'

    options['OTHER_PROJECTS'] = headerValues['COOKIES']['FEED_OPTION_OTHER_PROJECTS'] == 'Y' if 'FEED_OPTION_OTHER_PROJECTS' in headerValues['COOKIES'] else False

    if not options['OTHER_PROJECTS'] and headerValues['CURRENT_PROJECT']:
        result = result.filter(project=headerValues['CURRENT_PROJECT'])

    if options['MESSAGE_TYPE'] == 'SYSTEM_MESSAGES':
        result = result.filter(isSystemLog=True)

    if options['MESSAGE_TYPE'] == 'USER_MESSAGES':
        result = result.filter(filesExist=False, isSystemLog=False, commit__isnull=True, todo=False, bug=False)

    if options['MESSAGE_TYPE'] == 'FILES':
        result = result.filter(filesExist=True)

    if options['MESSAGE_TYPE'] == 'COMMITS':
        result = result.filter(commit__isnull=False)

    if options['MESSAGE_TYPE'] == 'TODO':
        result = result.filter(todo=True)

    if options['MESSAGE_TYPE'] == 'BUGS':
        result = result.filter(bug=True)

    if options['MESSAGE_TYPE'] == 'so':
        result = result.filter(type='so')

    if options['MESSAGE_TYPE'] == 'ro':
        result = result.filter(type='ro')

    if options['MESSAGE_TYPE'] == 'eo':
        result = result.filter(type='eo')

    if float(last_id) > 0:
        result = result.filter(id__lt=last_id)


    messages = []
    if last_id != 0:
        if options['MESSAGE_TYPE'] == 'TODO' or options['MESSAGE_TYPE'] == 'BUGS':
            result = result.order_by('checked', '-id')
        else:
            result = result.order_by('-id')

        result = result[:20]

        for message in result:
            addParams = {}
            if message.task and request.user.get_profile().isManager(message.task.project):
                addParams = {
                    'hidden_from_employee': message.hidden_from_employee,
                    'hidden_from_clients': message.hidden_from_clients
                }
            messages.append(message.getJson(addParams, request.user))

    templates = templateTools.getMessageTemplates()
    with file(settings.PROJECT_ROOT + 'tracker/templates/item_templates/messages/log_message.html') as f:
        templates['template'] = f.read()

    return {
        'messages': messages,
        'templates': templates,
        'options': options,
        'tab': True,
        'name': u'Лента'
    }
