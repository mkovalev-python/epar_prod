# -*- coding:utf-8 -*-
__author__ = 'Gvammer'

import json
from django.http import Http404
from django.db.models import Q
from django.db import transaction
# from tracker.settings import COMISSION
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.humanize.templatetags.humanize import intcomma
from django.shortcuts import HttpResponse, HttpResponseRedirect
from django.utils.timezone import now

from PManager.models import Specialty, PM_Task, PM_Timer, PM_Task_Message, PM_ProjectRoles, PM_Task_Status, PM_User, TaskDraft, \
    PM_Project, PM_Files, PM_Reminder
import datetime, json, codecs
from django.utils import timezone
from PManager.viewsExt import headers
from PManager.viewsExt.tools import taskExtensions, EmailMessage, templateTools
from PManager.classes.datetime.work_time import WorkTime
from PManager.classes.server.message import RedisMessage
from PManager.classes.logger.logger import Logger
from PManager.services.mind.task_mind_core import TaskMind
from PManager.services.projects import get_project_by_id
from PManager.services.task_drafts import get_unique_slug
from PManager.viewsExt.tools import redisSendTaskUpdate, service_queue, redisSendTaskAdd
from django.core.context_processors import csrf

FORMAT_TO_INTEGER = 1
CRITICALLY_THRESHOLD = 0.7


def task_ajax_action(fn):
    def new(*args):
        if len(args) > 1:
            raise Exception("Method should not take arguments.")
        return fn(*args)

    return new


def ajaxNewTaskWizardResponder(request):
    from django.shortcuts import render
    return render(request, 'task/new_task_wizard.html', {})


def microTaskAjax(request, task_id):
    try:
        task = PM_Task.objects.get(id=task_id)
        user = task.resp.get_profile() if task.resp else None
    except PM_Task.DoesNotExist:
        raise Http404
    except PM_User.DoesNotExist:
        raise Http404
    return HttpResponse(json.dumps({
        'id': task.id,
        'name': task.name,
        'executor': json.dumps(user.avatar_rel) if user is not None else '',
        'status': task.status.code
    }), content_type="application/json")


def __change_resp(request):
    task_id = int(request.POST.get('id', 0))  # переданный id задачи
    profile = request.user.get_profile()
    if not task_id:
        return 'bad query'
    try:
        task = PM_Task.objects.get(id=int(task_id))  # вот она, задачка
    except (ValueError, PM_Task.DoesNotExist):
        return 'bad query'

    if not task.canPMUserView(profile):
        return 'bad query'

    is_manager = profile.isManager(project=task.project)
    str_resp = request.POST.get('resp', False)
    if str_resp.find('@') > -1 and is_manager:
        task.resp = PM_User.getOrCreateByEmail(str_resp, task.project, 'employee')
    elif str_resp.find('@') == -1:
        try:
            resp_id = int(str_resp)
            task.resp = TaskWidgetManager.getResponsibleList(request.user, task.project).get(pk=resp_id)
        except User.DoesNotExist:
            from PManager.services.task_drafts import task_draft_is_user_participate
            user = task_draft_is_user_participate(task.id, resp_id, request.user.id)
            if user:
                task.resp = user
            else:
                return 'bad query'
        except ValueError:
            return 'bad query'
    else:
        return 'bad query'

    if task.parentTask:
        task.parentTask.observers.add(task.resp)

    r_prof = task.resp.get_profile()
    if not r_prof.hasRole(task.project):
        r_prof.setRole('employee', task.project)
        if r_prof.is_outsource:
            from PManager.models.agreements import Agreement
            Agreement.objects.get_or_create(payer=task.project.payer, resp=r_prof.user)

    # outsource
    if r_prof.is_outsource:  # if finance relationship
        task.setStatus('not_approved')
    else:
        task.closedInTime = False
        task.setStatus('revision')
    #end outsources
    task.lastModifiedBy = request.user

    task.save()
    resp = task.resp

    resp_name = ' '.join([resp.first_name, resp.last_name])
    response_text = {
        'resp': [{
                 'id': resp.id,
                 'name': resp_name,
                 'avatar': resp.get_profile().avatar_rel
                 }],
        'status': task.status.code,
        'critically': task.critically
    }
    response_text = json.dumps(response_text)

    if task.resp.email:
        ar_email = [task.resp.email if task.resp.id != request.user.id else None]

        task.sendTaskEmail('new_task', ar_email)

    task.systemMessage(
        u'изменен ответственный на ' + resp_name,
        request.user,
        'NEW_RESPONSIBLE'
    )
    redisSendTaskUpdate(
        {
            'resp': [{
                     'id': resp.id,
                     'name': resp_name,
                     'avatar': resp.get_profile().avatar_rel if resp else ''
                     }],
            'viewedOnly': request.user.id,
            'id': task.id
        }
    )
    return response_text


def __search_filter(header_values, request):
    # todo: как можно скорее перенести в actions
    from PManager.viewsExt.tools import templateTools
    from PManager.widgets.tasklist.widget import widget as task_list

    search_text, action, group = request.POST.get('task_search'), \
                                 request.POST.get('action', False), \
                                 request.POST.get('group', False)

    ar_filter = {}
    ar_exclude = {}
    if search_text:
        number = None
        if search_text.startswith(u'#') or search_text.startswith(u'№'):
            try:
                number = int(search_text
                             .replace(u'#', '')
                             .replace(u'№', '')
                             .replace(u' ', '')
                             )
            except ValueError:
                pass
        if number:
            ar_filter['number'] = number
        else:
            ar_filter['name__icontains'] = search_text
    qArgs = []
    if action == 'not_approved':
        ar_filter['status__code'] = 'not_approved'
        ar_filter['closed'] = False
    elif action == 'deadline':
        ar_filter['deadline__lt'] = datetime.datetime.now()
        ar_filter['deadline__isnull'] = False
        ar_filter['closed'] = False
    elif action == 'arc':
        ar_filter['closed'] = True
    elif action == 'ready':
        ar_filter['status__code'] = 'ready'
        ar_filter['closed'] = False
    elif action == 'not_ready':
        qArgs.append(Q(Q(status__in=PM_Task_Status.objects.exclude(code='ready')) | Q(status__isnull=True)))
        ar_filter['closed'] = False
    elif action == 'started':
        ar_filter['realDateStart__isnull'] = False
        ar_filter['closed'] = False
    elif action == 'all':
        pass


    kanbanFilter = None
    if 'gantt_props[]' in request.POST:
        propCodesKanban = request.POST.getlist('gantt_props[]')

        for propCode in propCodesKanban:
            if 'gantt_prop_' + propCode + '[]' in request.POST:
                propVals = request.POST.getlist('gantt_prop_' + propCode + '[]')
                for val in propVals:
                    if not kanbanFilter:
                        kanbanFilter = Q(**{propCode:val})
                    else:
                        kanbanFilter = kanbanFilter | Q(**{propCode:val})

    if kanbanFilter:
        qArgs.append(kanbanFilter)

    if 'withoutParent' in request.POST:
        if request.POST['withoutParent'] == 'Y':
            ar_filter['isParent'] = False

    if 'responsible[]' in request.POST:
        ar_filter['resp__in'] = request.POST.getlist('responsible[]')
    if 'observers[]' in request.POST:
        ar_filter['observers__in'] = request.POST.getlist('observers[]')
    if 'author[]' in request.POST:
        ar_filter['author__in'] = request.POST.getlist('author[]')
    if 'closed[]' in request.POST:
        ar_closed_flags = request.POST.getlist('closed[]')
        if 'N' not in ar_closed_flags:
            ar_filter['closed'] = True
        elif 'Y' not in ar_closed_flags:
            ar_filter['closed'] = False
    if 'viewed[]' in request.POST:
        a_viewed_flags = request.POST.getlist('viewed[]')
        if 'N' not in a_viewed_flags:
            ar_filter['viewedUsers'] = request.user
        elif 'Y' not in a_viewed_flags:
            ar_exclude['viewedUsers'] = request.user
    dates_tmp = []
    if 'date_create[]' in request.POST:
        dates_tmp.append({
            'date': request.POST.getlist('date_create[]'),
            'key': 'dateCreate'
        })
    if 'date_modify[]' in request.POST:
        dates_tmp.append({
            'date': request.POST.getlist('date_modify[]'),
            'key': 'dateModify'
        })
    if 'date_close[]' in request.POST:
        dates_tmp.append({
            'date': request.POST.getlist('date_close[]'),
            'key': 'dateClose'
        })
    if 'color[]' in request.POST:
        arColors = request.POST.getlist('color[]')
        ar_filter['color__in'] = arColors

    if dates_tmp:
        for dateTmp in dates_tmp:
            if len(dateTmp['date']) == 1:  # only one date
                date = templateTools.dateTime.convertToDateTime(dateTmp['date'][0])
                ar_filter[dateTmp['key'] + '__gt'] = date
                ar_filter[dateTmp['key'] + '__lt'] = date + datetime.timedelta(days=1)
            elif len(dateTmp['date']) == 2:  # from - to
                filter_date_from_tmp = templateTools.dateTime.convertToDateTime(dateTmp['date'][0])
                filter_date_to_tmp = templateTools.dateTime.convertToDateTime(dateTmp['date'][1])
                ar_filter[dateTmp['key'] + '__gt'] = filter_date_from_tmp
                ar_filter[dateTmp['key'] + '__lt'] = filter_date_to_tmp + datetime.timedelta(days=1)

    if 'parent' in request.POST:
        ar_filter['parentTask'] = request.POST.get('parent')

    if 'milestone_id' in request.POST:
        if request.POST['milestone_id']:
            ar_filter['milestone'] = int(request.POST['milestone_id'])

    if action == 'deadline':
        qArgs.append(
            Q(
                Q(deadline__lt=datetime.datetime.now()),
                Q(closed=False)
            ) | Q(dateClose__lt=datetime.datetime.now())
        )

    needXlsOutput = request.POST.get('xls') and header_values['CURRENT_PROJECT'] or False
    ar_page_params = {}
    if not needXlsOutput:
        page, count, start_page = int(request.POST.get('page', 1)), 10, int(request.POST.get('startPage', 0))
        if start_page:
            page = start_page

        if start_page:
            count *= page
            page = 1

        if page:
            idExclude = request.POST.getlist('idExclude[]', [])
            if len(idExclude):
                ar_exclude['id__in'] = []
                for idEx in idExclude:
                    ar_exclude['id__in'].append(int(idEx))

                page = 1

        ar_page_params = {
            'pageCount': count,
            'page': page,
            'startPage': start_page,
            'group': group
        }


    tasks = task_list(
        request,
        header_values,
        {
            'filter': ar_filter,
            'exclude': ar_exclude
        },
        qArgs,
        ar_page_params
    )

    if needXlsOutput:
        response_text = json.dumps(
            {
                'file':
                    str(__save_xls_from_task_list(tasks['tasks'], header_values['CURRENT_PROJECT'], request.user))
            }
        )
    else:
        paginator = tasks['paginator']
        tasks = tasks['tasks']
        response_text = json.dumps({'tasks': list(tasks), 'paginator': paginator})

    return response_text


def __save_xls_from_task_list(task_list, project, user):
    if not project:
        return None

    import xlsxwriter
    import StringIO
    from django.core.files.base import ContentFile

    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)

    ws = workbook.add_worksheet('sumLoan')

    bold = workbook.add_format({'bold': 1})
    date_format = workbook.add_format({'num_format': 'd mmmm yyyy h:mm:ss'})
    url_format = workbook.add_format({'color': 'green', 'underline': 1})

    row = 0
    col = 0

    for title in [
        u'Дата',
        u'Ответственный',
        u'Позиция',
        u'Время',
        u'План',
        u'Результат',
        u'Закрыта',
        u'Дата закрытия',
        u'Описание',
    ]:

        ws.write(row, col, title, bold)
        col += 1

    ws.set_column(0, 2, 20)  # first 3 columns width
    col = 0
    row = 1

    for item in task_list:
        date = item.get('last_message', {}).get('date', '')
        ws.write_string(
            row,
            col,
            date
        )
        ws.write_string(row, col + 1, item.get('resp', [])[0].get('name', ''))
        ws.write_url(row, col + 2, settings.HTTP_ROOT_URL + item.get('url', ''), url_format, item.get('name', ''))
        timeObj = templateTools.dateTime.timeFromTimestamp(item.get('time', 0))
        ws.write_string(
            row,
            col + 3,
            (
                ('0' if len(str(timeObj['hours'])) == 1 else '') + str(timeObj['hours']) + ':' +
                ('0' if len(str(timeObj['minutes'])) == 1 else '') + str(timeObj['minutes']) + ':' +
                ('0' if len(str(timeObj['seconds'])) == 1 else '') + str(timeObj['seconds'])
            )
        )
        ws.write_string(row, col + 4, str(item.get('planTime', '')).replace('.', ',') or '')
        ws.write_string(row, col + 5, item.get('last_message', {}).get('text', '') or '')
        ws.write_string(row, col + 6, u'Да' if item.get('closed', None) else u'')
        ws.write_string(row, col + 7, item.get('dateClose', '') or '')
        ws.write_string(row, col + 8, item.get('text', '') or '')
        # ws.write_number(row, col + 3, item.get('text', ''))
        row += 1

    workbook.close()

    xlsx_data = output.getvalue()
    file = PM_Files(
        projectId=project,
        authorId=user,
        name=str(user) + str(project)
    )
    file.save()
    file.file.save(
        'projects/' + str(int(project.id)) + '/stat/' + str(file.id) + '.xls',
        ContentFile(xlsx_data)
    )
    file.save()

    return file.src

def __save_doc_from_task_list(task_list):
    from docxtpl import DocxTemplate

    doc = DocxTemplate("./tracker/media/company2.docx")
    context = {'company_name': "12123"}
    doc.render(context.decode('utf-8'))
    src = "./tracker/media/Report_" + datetime.datetime.now().strftime(
        "%d_%m_%Y_%H:%M") + ".docx"

    doc.save(src)

    return "/protected/media/Report_" + datetime.datetime.now().strftime("%d_%m_%Y_%H:%M") + ".docx"

def __save_xls_tree_from_task_list(task_list, project, user):
    if not project:
        return None

    import xlsxwriter
    import StringIO
    from django.core.files.base import ContentFile

    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)

    ws = workbook.add_worksheet('sumLoan')

    bold = workbook.add_format({'bold': 1})
    date_format = workbook.add_format({'num_format': 'd mmmm yyyy h:mm:ss'})
    url_format = workbook.add_format({'color': 'green', 'underline': 1})

    row = 0
    col = 0

    for title in [
        u'Дата',
        u'ID',
        u'Название',
        u'Исполнитель',
        u'Сетевая организация',
        u'Регулирующий орган',
        u'Экспертная организация',
    ]:

        ws.write(row, col, title, bold)
        col += 1

    ws.set_column(0, 2, 20)  # first 3 columns width
    col = 0
    row = 1

    for item in task_list:
        date = datetime.datetime.strftime(item.dateCreate, '%Y-%m-%d %H:%M')
        ws.write_string(
            row,
            col,
            date
        )
        ws.write_string(row, col + 1, str(item.id))
        ws.write_url(row, col + 2, settings.HTTP_ROOT_URL + item.url, url_format, item.prefix + ' ' + item.name)
        ws.write_string(row, col + 3, ' '.join([item.resp.last_name, item.resp.first_name]) if item.resp else '')
        i = 3
        for x in [
            item.planTimeMainOrg,
            item.planTimeRegulator,
            item.planTime,
        ]:
            i += 1
            if x:
                ws.write_number(row, col + i, x)
            else:
                ws.write_string(row, col + i, '')

        row += 1

    workbook.close()

    xlsx_data = output.getvalue()
    file = PM_Files(
        projectId=project,
        authorId=user,
        name=str(user) + str(project)
    )
    file.save()
    file.file.save(
        'projects/' + str(int(project.id)) + '/stat/' + str(file.id) + '.xls',
        ContentFile(xlsx_data)
    )
    file.save()

    return file.src


def __task_message(request):
    text = request.POST.get('task_message', '')
    task_id = request.POST.get('task_id', '')
    to = request.POST.get('to', None)
    type = request.POST.get('type', "so")
    task_close = request.POST.get('close', '') == 'Y'
    b_resp_change = request.POST.get('responsible_change', '') == 'Y'
    hidden = (request.POST.get('hidden', '') == 'Y' and to)
    requested_time = float(request.POST.get('need-time-hours', 0)) if (request.POST.get('need-time', '') == 'Y') else 0
    solution = (request.POST.get('solution', 'N') == 'Y')
    task = PM_Task.objects.get(id=task_id)
    profile = request.user.get_profile()
    is_manager = profile.isManager(task.project)
    hidden_from_employee = False
    hidden_from_clients = False
    if is_manager:  # TODO: разобраться с тем, как должно работать скрытие от автора
        hidden_from_clients = request.POST.get('hidden_from_clients', '') == 'Y'
        hidden_from_employee = request.POST.get('hidden_from_employee', '') == 'Y'
    project_settings = task.project.getSettings()
    if project_settings.get('autohide_messages', False):
        if profile.isEmployee(task.project):
            hidden_from_clients = True
        elif profile.isClient(task.project):
            hidden_from_employee = True
    status = request.POST.get('status', '') if request.POST.get('status', '') in ['ready', 'revision'] else None
    uploaded_files = request.POST.getlist('files') if 'files' in request.POST else []
    author = request.user
    response_text = ''

    if task:
        text = text.replace('<', '&lt;').replace('>', '&gt;')
        message = PM_Task_Message(text=text, task=task, author=author, solution=solution, type=type)
        # message = PM_Task_Message(text=text, task=task, author=author, solution=solution, tab=tab)
        message.hidden = hidden
        message.hidden_from_clients = hidden_from_clients
        message.hidden_from_employee = hidden_from_employee
        message.requested_time = requested_time
        if requested_time > 0:
            message.code = 'TIME_REQUEST'

        if to:
            try:
                to = User.objects.get(pk=int(to))
                if to.get_profile().hasRole(
                        task.project):  # todo здесь надо заменить на проверку, есть ли адресат в команде текущего пользователя
                    if b_resp_change:
                        task.resp = to
                        task.save()
                    task.observers.add(to)
                    message.userTo = to
            except User.DoesNotExist:
                pass

        message.save()

        task.setChangedForUsers(request.user)
        if status:
            task.setStatus(status)
            logger = Logger()
            logger.log(request.user, 'STATUS_' + status.upper(), 1, task.project.id)

        bFilesExist = False
        for filePost in uploaded_files:
            try:
                file_obj = PM_Files.objects.get(pk=filePost)
                message.files.add(file_obj)
                bFilesExist = True
            except PM_Files.DoesNotExist():
                pass

        if bFilesExist:
            message.filesExist = bFilesExist
            message.save()

        if solution:
            from wiking.services.articles import ArticleService
            article = ArticleService.get_article(
                None,
                message.task.id,
                message.task.project
            )
            articleData = {
                    'project': message.task.project,
                    'slug': message.task.id,
                    'title': message.task.name,
                    'comment': u'Расчет №' + str(message.task.number),
                    'content': message.text,
                    'parent': None
                }
            if article:
                ArticleService.update_article(article, articleData, author)
            else:
                ArticleService.create_article(
                    articleData,
                    author
                )
        ar_email = task.getUsersEmail([author.id])

        if hidden:
            ar_email = [to.email]
        else:
            if hidden_from_clients:
                while task.author and \
                        task.author.is_active and \
                        task.author.email and \
                                task.author.email in ar_email:
                    ar_email.remove(task.author.email)

            if hidden_from_employee:
                if task.resp:
                    while task.resp.email and task.resp.email in ar_email:
                        ar_email.remove(task.resp.email)

        if to and hasattr(to, 'email'):
            ar_email.append(to.email)

        task_data = {
            'task_url': message.task.url,
            'name': message.project.name + '. ' + message.task.name,
            'dateCreate': timezone.make_aware(datetime.datetime.now(), timezone.get_current_timezone()),
            'message': {
                'text': message.text,
                'author': ' '.join([message.author.first_name, message.author.last_name]),
                'file_list': taskExtensions.getFileList(message.files.all())
            }
        }

        mail_sender = EmailMessage(
            'new_task_message',
            {
                'task': task_data
        },
            u'Сообщение: ' + task_data['name']
        )

        try:
            mail_sender.send(ar_email)
        except Exception:
            print 'Email has not sent'

        response_json = message.getJson({
            'canEdit': message.canEdit(request.user),
            'canDelete': message.canDelete(request.user),
            'noveltyMark': True
        })

        mess = RedisMessage(service_queue,
                            objectName='comment',
                            type='add',
                            fields=response_json)
        mess.send()

        task_update_push_data = {'viewedOnly': request.user.id, 'id': task.id}
        if status:
            task_update_push_data['status'] = status
        redisSendTaskUpdate(task_update_push_data)
        response_text = json.dumps(response_json)

    return response_text

def taskListXls1(request,st):
    header_values = headers.initGlobals(request)
    if not request.user.is_authenticated():
        raise Http404

    ar = []

    def a(t):
        n = True
        while t and n:
            yield t

            if t.parentTask:
                t = t.parentTask
            else:
                n = False

    tasks = PM_Task.objects.select_related('parentTask').filter(active=True, project=header_values['CURRENT_PROJECT'])
    for task in tasks:
        setattr(task, 'prefix', ''.join(reversed(['1' for y in a(task)])))
        ar.append(task)

    ar.sort(key=lambda x: '_'.join(reversed([str(y.id) for y in a(x)])))
    if st:
        return ar
    test_path = __save_doc_from_task_list(ar)
    # path = __save_xls_tree_from_task_list(ar, header_values['CURRENT_PROJECT'], request.user)
    return HttpResponseRedirect(test_path)

def taskListXls(request):
    header_values = headers.initGlobals(request)
    if not request.user.is_authenticated():
        raise Http404

    ar = []

    def a(t):
        n = True
        while t and n:
            yield t

            if t.parentTask:
                t = t.parentTask
            else:
                n = False

    tasks = PM_Task.objects.select_related('parentTask').filter(active=True, project=header_values['CURRENT_PROJECT'])
    for task in tasks:
        setattr(task, 'prefix', ''.join(reversed(['1' for y in a(task)])))
        ar.append(task)

    ar.sort(key=lambda x: '_'.join(reversed([str(y.id) for y in a(x)])))

    path = __save_doc_from_task_list(ar)
    # path = __save_xls_tree_from_task_list(ar, header_values['CURRENT_PROJECT'], request.user)
    return HttpResponseRedirect(path)

def taskListAjax(request):
    from PManager.models import PM_Files, PM_User_PlanTime, PM_Task_Status

    header_values = headers.initGlobals(request)
    ajax_task_manager = taskAjaxManagerCreator(request)

    if not request.user.is_authenticated():
        response_text = json.dumps({'unauthorized': True})

    elif ajax_task_manager.tryToSetActionFromRequest():
        ajax_task_manager.process()
        response_text = ajax_task_manager.getResponse()

    elif 'resp' in request.POST:  # смена ответственного
        response_text = __change_resp(request)

    elif request.POST.get('task_search', False) or \
            request.POST.get('action', False) or \
            request.POST.get('parent', False):
        response_text = __search_filter(header_values, request)

    elif 'task_message' in request.POST:
        response_text = __task_message(request)

    elif 'get_endtime' in request.POST:
        task_timer = WorkTime(taskHours=request.POST.get('plan_time', False),
                             startDateTime=timezone.make_aware(datetime.datetime.now(),
                                                               timezone.get_default_timezone()))
        result = templateTools.dateTime.convertToDateTime(task_timer.endDateTime)
        response_text = json.dumps({'endDate': 4})

    elif request.POST.get('prop', False):
        property = request.POST.get('prop', False)
        task_id = request.POST.get('id', False)
        value = request.POST.get('val', False)
        if property and task_id:
            task = PM_Task.objects.get(id=task_id)
            sendData = {}
            if task:
                if property == "planTimeRegulator" and value:
                    task.planTimeRegulator = value
                    task.save()
                elif property == "planTimeMainOrg" and value:
                    task.planTimeMainOrg = value
                    task.save()
                elif property == "planTime" and value:
                    task.lastModifiedBy = request.user
                    task.setPlanTime(value, request)
                    from PManager.services.rating import get_user_rating_for_task
                    task.systemMessage(
                        u'оценил(а) позицию в ' + str(value) + u' руб. с компетентностью '
                        + str(get_user_rating_for_task(task, request.user)),
                        request.user,
                        'SET_PLAN_TIME'
                    )
                    sendData['critically'] = task.critically

                elif property == "to_plan":
                    task.onPlanning = True
                    sendData['onPlanning'] = True
                    task.save()

                elif property == "from_plan":
                    task.onPlanning = False
                    sendData['onPlanning'] = False
                    planTimes = PM_User_PlanTime.objects.filter(task=task).order_by('time')
                    for planTime in planTimes:
                        if planTime.user.get_profile().isEmployee(task.project):
                            task.planTime = planTime.time
                            break
                    task.save()

                elif property == "deadline":
                    deadline_date = value
                    reminder_date = request.POST.get('reminder', False)
                    sendData['deadline'] = deadline_date
                    sendData['reminder'] = reminder_date

                    if deadline_date:
                        deadline_date = templateTools.dateTime.convertToDateTime(deadline_date)
                        task.deadline = deadline_date
                    else:
                        task.deadline = None
                        sendData['deadline'] = False
                    task.save()

                    if reminder_date:
                        reminder_date = templateTools.dateTime.convertToDateTime(reminder_date)
                    else:
                        reminder_date = None
                    try:
                        task_reminder = PM_Reminder.objects.get(task=task)
                        task_reminder.date = reminder_date
                        if reminder_date:
                            task_reminder.save()
                        else:
                            task_reminder.delete()
                            sendData['reminder'] = False
                    except PM_Reminder.DoesNotExist:
                        if reminder_date:
                            task_reminder = PM_Reminder(task=task, date=reminder_date, user=request.user)
                            task_reminder.save()

                elif property == "critically":
                    value = float(value)
                    bCriticallyIsGreater = task.critically < value
                    task.critically = value
                    task.lastModifiedBy = request.user
                    task.save()
                    task.systemMessage(
                        u'Критичность ' + (u'повышена' if bCriticallyIsGreater else u'понижена'),
                        request.user,
                        'CRITICALLY_' + ('UP' if bCriticallyIsGreater else 'DOWN')
                    )
                    sendData['critically'] = task.critically

                elif property == "color":
                    sendData['color'] = value
                    task.color = value
                    task.save()

                elif property == "status":
                    if task.status and task.status.code == 'not_approved':
                        try:
                            if task.resp.get_profile().is_outsource:
                                if not task.planTime:
                                    return HttpResponse(json.dumps({
                                        'error': u'расчет должен быть оценен'
                                    }))

                                if request.user.id == task.project.payer.id or request.user.get_profile().isManager(task.project):
                                    if task.resp.get_profile().getBet(task.project) * task.planTime > task.project.payer.get_profile().account_total + int(task.project.payer.get_profile().overdraft or 0):
                                        return HttpResponse(json.dumps({
                                            'error': u'У ' +
                                                     task.project.payer.last_name + u' ' + task.project.payer.first_name +
                                                     u' недостаточно средств для подтверждения задачи'
                                        }))
                                else:
                                    return HttpResponse(json.dumps({
                                        'error': u'расчет может подтвердить только ' +
                                                 task.project.payer.last_name + u' ' + task.project.payer.first_name
                                    }))

                            if not request.user.get_profile().isManager(task.project):
                                return HttpResponse(json.dumps({
                                    'error': u'расчет может подтвердить только менеджер'
                                }))

                        except PM_ProjectRoles.DoesNotExist:
                            pass
                    #\client have not enough money#

                    try:
                        if value == 'ready':
                            task.setIsInTime()
                        else:
                            task.closedInTime = False

                        task.setStatus(str(value))

                        task.systemMessage(
                            u'Статус изменен на "' + task.status.name + u'"',
                            request.user,
                            'STATUS_' + task.status.code.upper()
                        )
                        sendData['status'] = task.status.code
                        logger = Logger()
                        logger.log(request.user, 'STATUS_' + task.status.code.upper(), 1, task.project.id)

                    except PM_Task_Status.DoesNotExist:
                        pass

                if len(sendData) > 0:
                    sendData['id'] = task.pk
                    sendData['viewedOnly'] = request.user.id
                    redisSendTaskUpdate(sendData)

                response_text = json.dumps(sendData)
            else:
                response_text = 'none'
        else:
            response_text = 'none'
    else:
        response_text = 'bad query'

    return HttpResponse(response_text)


class taskManagerCreator:
    task = None
    parentTask = None
    project = None
    fileList = []
    currentUser = None

    def __init__(self, id=None, currentUser=None):
        if id:
            try:
                self.task = PM_Task.objects.get(id=id)
            except PM_Task.DoesNotExist:
                pass

        if currentUser:
            self.currentUser = currentUser

    def fastCreateAndGetTask(self, text):
        self.task = PM_Task.createByString(text, self.currentUser, self.fileList, self.parentTask, project=self.project)
        self.task.systemMessage(u'Добавлено', self.currentUser, 'TASK_CREATE')

        if self.task.resp and self.task.resp.get_profile().is_outsource:
            self.task.setStatus('not_approved')
        else:
            self.task.setStatus('revision')

        return self.task

    def stopUserTimersAndPlayNew(self):
        if self.task and self.currentUser:
            if self.task.status and self.task.status.code == 'not_approved':
                return False

            timers = PM_Timer.objects.filter(user=self.currentUser, dateEnd=None)
            for timer in timers:
                timer.task.endTimer(self.currentUser,
                                    'Change task to <a href="' + self.task.url + '">#' + str(self.task.id) + '</a>')
                timer.task.Stop()

            if not self.task.deadline and self.task.planTime and self.task.critically > CRITICALLY_THRESHOLD:
                taskTimer = WorkTime(
                                     taskHours=self.task.planTime,
                                     startDateTime=timezone.make_aware(datetime.datetime.now(),
                                                                       timezone.get_default_timezone()),
                                     userHoursPerDay=self.currentUser.get_profile().hoursQtyPerDay
                            )
                self.task.deadline = taskTimer.endDateTime #will be saved in 'Start' method

            self.task.startTimer(self.currentUser) #запускаем таймер
            self.task.Start()
            return True
        else:
            return False

    def getSimilar(self, text):
        return PM_Task.getSimilar(text, self.project)

    def closeTask(self):
        if self.task:
            pass
        else:
            return False

    def stopTimer(self, comment):
        if self.task:
            self.task.Stop()
            self.task.endTimer(None, comment) #или останавливаем и сохраняем очередной
            return True
        else:
            return False

    def addMessage(self, message, solution=0):
        if solution == 1:
            code = "SOLUTION"
        else:
            code = ""
        message = PM_Task_Message(text=u'Затраченное время: ' + unicode(self.task.currentTimer) + u"\r\nЧто сделано: " + message, task=self.task,
                                  author=self.currentUser, solution=solution, code=code)
        message.save()
        responseJson = message.getJson({
            'canEdit': message.canEdit(self.currentUser),
            'canDelete': message.canDelete(self.currentUser),
            'noveltyMark': True
        })

        mess = RedisMessage(service_queue,
                            objectName='comment',
                            type='add',
                            fields=responseJson
        )
        mess.send()

        self.sendEmailAboutNewMessage(message)

    def tryToRemoveMessage(self, id):
        try:
            message = PM_Task_Message.objects.get(id=id, author=self.currentUser)
            message.delete()
            return True
        except PM_Task_Message.DoesNotExist:
            return False

    def sendEmailAboutNewMessage(self, messageObject):
        if not self.project:
            self.project = messageObject.task.project

        arEmail = self.task.getUsersEmail(
            [self.currentUser.id] +
            list(self.project.projectRoles.filter(role__code='guest').values_list('user__id', flat=True))
        )

        if messageObject.userTo:
            if self.currentUser.id != messageObject.userTo.id:
                arEmail.append(messageObject.userTo.email)

        #send message to all managers
        #if it is client's message
        if messageObject.task and \
                messageObject.author.id == messageObject.task.project.payer.id:
            for user in User.objects.filter(
                    pk__in=PM_ProjectRoles.objects.filter(
                            role__code='manager', project=messageObject.task.project
                    ).values('user__id')
            ):
                arEmail.append(user.email)

        taskdata = {
            'task_url': messageObject.task.url,
            'name': messageObject.task.name,
            'dateCreate': timezone.make_aware(datetime.datetime.now(), timezone.get_current_timezone()),
            'time': unicode(self.task.currentTimer),
            'message': {
                'text': messageObject.text,
                'author': ' '.join([messageObject.author.first_name, messageObject.author.last_name]),
                'file_list': taskExtensions.getFileList(messageObject.files.all())
            }
        }

        sendMes = EmailMessage('new_task_message',
                               {
                                   'task': taskdata
                               },
                               'Новое сообщение в вашей задаче!'
                               )

        try:
            sendMes.send(arEmail)
        except Exception:
            print 'Message doesn\'t send'


#todo: заменить все действия в taskListAjax на методы данного класса
class taskAjaxManagerCreator(object):
    action = None
    result = None
    taskManager = None
    globalVariables = None
    currentUser = None
    request = None

    def __init__(self, request):
        from PManager.widgets.tasklist.widget import widget as taskList

        self.globalVariables = headers.initGlobals(request)
        self.action = request.POST.get('action', None)
        self.currentUser = request.user
        self.request = request
        self.taskListWidget = taskList
        self.initTaskManager(request)

    def getRequestData(self, key=None, format=None):
        if not key:
            return self.request
        elif key in self.request.POST:
            result = self.request.POST[key]
            if format == FORMAT_TO_INTEGER:
                try:
                    result = int(result)
                except:
                    result = 0
            return result
        else:
            return None

    def tryToSetActionFromRequest(self):
        action = self.getRequestData('action')
        if action and hasattr(self, ('process_' + action)):
            self.action = action
            return True
        else:
            return False

    def setActionName(self, actionName):
        self.action = actionName

    def initTaskManager(self, request):
        task_id = self.getRequestData('id', FORMAT_TO_INTEGER)

        taskManager = taskManagerCreator(task_id, request.user)
        taskManager.project = self.globalVariables['CURRENT_PROJECT']
        if 'parent' in request.POST:
            taskManager.parentTask = request.POST['parent']

        if 'files[]' in request.POST:
            taskManager.fileList = request.POST.getlist('files[]')

        self.taskManager = taskManager

    def process(self):
        if self.action:
            self.doAction()

    def doAction(self):
        if hasattr(self, 'process_' + self.action):
            self.result = self.__getattribute__('process_' + self.action)()

    def getResponse(self):
        if self.result:
            return HttpResponse(self.result)

    @task_ajax_action
    def process_inviteUsers(self):
        from PManager.viewsExt.task_drafts import taskdraft_resend_invites
        task_ids = self.request.POST.getlist('tasks[]')
        tags = self.request.POST.getlist('tag[]') if 'tag[]' in self.request.POST else []
        title = self.request.POST.get('title', '')
        project_id = self.request.POST.get('project', None)
        project = get_project_by_id(project_id)
        if project is None:
            return HttpResponse(json.dumps({'error': 'Не выбран проект'}))

        tasks = PM_Task.objects.filter(id__in=task_ids)
        slug = get_unique_slug()
        task_draft = TaskDraft.objects.create(author=self.currentUser, slug=slug, title=title, project=project)

        for tagName in tags:
            spec, created = Specialty.objects.get_or_create(name=tagName)

            if spec.id:
                task_draft.specialties.add(spec)

        for task in tasks:
            if not task.canEdit(self.currentUser):
                continue

            task.onPlanning = True
            task.resp = None
            task.save()

            redisSendTaskUpdate({
                'id': task.id,
                'onPlanning': True
            })
            task_draft.tasks.add(task)

        task_draft.status = TaskDraft.OPEN
        task_draft.save()

        return taskdraft_resend_invites(self.request, task_draft.slug)

        # return HttpResponse(json.dumps({'result': 'OK', 'slug': slug}))

    @task_ajax_action
    def process_getEndTime(self):
        plan = self.request.POST.get('plan_time', False)
        task_timer = WorkTime(taskHours=float(plan),
                             startDateTime=timezone.make_aware(datetime.datetime.now(),
                                                               timezone.get_default_timezone()))

        pretty = templateTools.dateTime.convertToSite(task_timer.endDateTime)
        date = templateTools.dateTime.convertToDb(task_timer.endDateTime)

        return HttpResponse(json.dumps({'endDate': pretty, 'endDateForCheck': date}))

    @task_ajax_action
    def process_baneUser(self):
        from PManager.models import Credit
        t = self.taskManager.task
        user = self.currentUser
        if t.canEdit(user):
            for timer in PM_Timer.objects.filter(user=t.resp, task=t):
                timer.delete()
            for credit in Credit.objects.filter(user=t.resp, task=t):
                credit.delete()
            t.resp = None
            t.save()
            return HttpResponse(json.dumps({'result': 'OK'}))

        return HttpResponse(json.dumps({'result': 'ERROR'}))

    @task_ajax_action
    def process_ganttAjax(self):
        from PManager.widgets.gantt.widget import widget as gantt

        aFilter = {}
        if 'date_create[]' in self.request.POST:
            aDatesTmp = self.request.POST.getlist('date_create[]')
            filterDateFromTmp = templateTools.dateTime.convertToDateTime(aDatesTmp[0])
            filterDateToTmp = templateTools.dateTime.convertToDateTime(aDatesTmp[1])
            aFilter['realDateStart__gt'] = filterDateFromTmp
            aFilter['realDateStart__lt'] = filterDateToTmp + datetime.timedelta(days=1)
        hValues = {}
        if 'project' in self.request.POST:
            hValues['CURRENT_PROJECT'] = self.request.POST.get('project')

        result = gantt(self.request, hValues, {'filter': aFilter})
        return json.dumps({
            'tasks': list(result['tasks'])
        })

    @task_ajax_action
    def process_taskOpen(self):
        t = self.taskManager.task
        user = self.currentUser
        if t.closed:
            t.Open()
            if t.resp:
                if not t.resp.is_active:
                    t.resp = False
                    t.save()

            if t.parentTask and t.parentTask.closed:
                t.parentTask.Open()

            t.systemMessage(u'Проведено', user, 'TASK_OPEN')

        return json.dumps({
            'closed': t.closed
        })

    @task_ajax_action
    def process_taskClose(self):
        t = self.taskManager.task
        user = self.currentUser
        error = ''

        if t.started:
            t.Stop()
            t.endTimer(user, u'Закрытие задачи')

        if not t.closed:
            profile = user.get_profile()
            bugsExists = t.messages.filter(bug=True, checked=False).exists()
            if bugsExists:
                text = u'Перед тем как утвердить расчет, вам нужно исправить все ошибки.'
                message = PM_Task_Message(text=text, task=t, project=t.project, author=t.resp,
                                          userTo=user, code='WARNING', hidden=True)
                message.save()
                responseJson = message.getJson()

                mess = RedisMessage(
                    service_queue,
                    objectName='comment',
                    type='add',
                    fields=responseJson
                )
                mess.send()
            else:
                if profile.isClient(t.project) or profile.isManager(t.project) or t.author.id == user.id:
                    taskTimers = PM_Timer.objects.filter(task=t)
                    if taskTimers.count():
                        if t.resp and t.resp.get_profile().is_outsource:
                            if not user or user.id != t.project.payer.id:
                                error = u'Закрывать задачи с участием PRO специалистов может только ' + \
                                    t.project.payer.last_name + ' ' + t.project.payer.first_name

                            from PManager.models.agreements import Agreement
                            from django.db.models import Count

                            taskTimers = taskTimers.values('user__id').annotate(dcount=Count('user__id'))
                            for timer in taskTimers:
                                if timer['user__id'] == t.project.payer.id:
                                    continue

                                u = User.objects.get(pk=timer['user__id'])
                                try:
                                    agreement = Agreement.objects.get(
                                        approvedByPayer=True,
                                        approvedByResp=True,
                                        resp=u,
                                        payer=t.project.payer
                                    )
                                except Agreement.DoesNotExist:
                                    error = u'Нет принятого с обоих сторон договора c ' + u.last_name + ' ' + u.first_name

                    if not error:
                        if not t.closedInTime:
                            t.setIsInTime()

                        t.Close(user)
                        t.systemMessage(u'Расчет проведен', user, 'TASK_CLOSE')

                        #TODO: данный блок дублируется 4 раза
                        # if t.milestone and not t.milestone.closed:
                        #     qtyInMS = PM_Task.objects.filter(active=True, milestone=t.milestone, closed=False)\
                        #         .exclude(id=t.id).count()
                        #
                        #     if not qtyInMS:
                        #         t.milestone.close_milestone(date=datetime.datetime.now(), user=t.milestone.manager)

                        if t.parentTask and not t.parentTask.closed:
                            c = t.parentTask.subTasks.filter(closed=False, active=True).count()
                            if c == 0:
                                t.parentTask.Close(user)
                                # if t.parentTask.milestone and not t.parentTask.milestone.closed:
                                #     qtyInMS = PM_Task.objects.filter(active=True, milestone=t.parentTask.milestone,
                                #                                      closed=False).count()
                                #     if not qtyInMS:
                                #         milestone = t.parentTask.milestone
                                #         milestone.close_milestone(now(), user)

                        else:
                            for stask in t.subTasks.all():
                                if stask.started:
                                    stask.Stop()
                                    stask.endTimer(user, u'Закрытие задачи')

                                stask.Close(user)

                        net = TaskMind()
                        net.train([t])

                        sendMes = EmailMessage('task_closed', {'task': t}, u'Позиция закрыта: ' + t.name)
                        sendMes.send([t.author.email, t.resp.email])

                elif (not t.status) or t.status.code != 'ready':
                    t.setIsInTime()
                    t.setStatus('ready')

                    t.systemMessage(
                        u'Статус изменен на "' + t.status.name + u'"',
                        user,
                        'STATUS_' + t.status.code.upper()
                    )

        return json.dumps({
            'closed': t.closed,
            'status': t.status.code if t.status else None,
            'error': error
        })

    @task_ajax_action
    def process_startObserve(self):
        obs = self.taskManager.task.observers.all()
        if self.currentUser.id not in [u.id for u in obs]:
            self.taskManager.task.observers.add(self.currentUser)

        return json.dumps({'success': 'Y'})

    @task_ajax_action
    def process_stopObserve(self):
        obs = self.taskManager.task.observers.all()
        if self.currentUser.id in [u.id for u in obs]:
            self.taskManager.task.observers.remove(self.currentUser)

        return json.dumps({'success': 'Y'})

    @task_ajax_action
    def process_removeMessage(self):
        id = self.getRequestData('id')
        if self.taskManager.tryToRemoveMessage(id):
            return json.dumps({'success': 'Y'})

    @task_ajax_action
    def process_taskPlay(self):
        if self.taskManager.stopUserTimersAndPlayNew():
            task = self.taskManager.task
            aResult = {'started': True}
            if task.deadline:
                aResult['deadline'] = templateTools.dateTime.convertToSite(task.deadline)
            return json.dumps(aResult)
        else:
            return json.dumps({'error': 'Расчет не подтвержден'})

    @task_ajax_action
    def process_taskStop(self):
        comment = self.getRequestData('comment')
        public = self.getRequestData('public', FORMAT_TO_INTEGER)
        solution = self.getRequestData('solution', FORMAT_TO_INTEGER)

        if self.taskManager.stopTimer(comment):
            if public and public > 0 and comment:
                self.taskManager.addMessage(comment, solution)

            self.taskManager.task.setChangedForUsers(self.currentUser)
            return 'ok'

    @task_ajax_action
    def process_getSimilar(self):
        text = self.getRequestData('text')
        tasks = self.taskManager.getSimilar(text)
        return json.dumps([{'name': task.name, 'url': task.url} for task in tasks])

    @task_ajax_action
    def process_fastCreate(self):
        taskInputText = self.getRequestData('task_name')
        request = self.getRequestData()
        if taskInputText:
            task = self.taskManager.fastCreateAndGetTask(taskInputText)

            if task:
                task.lastModifiedBy = self.currentUser
                taskListWidgetData = self.taskListWidget(request, self.globalVariables, {'filter': {'id': task.id}})
                tasks = taskListWidgetData['tasks']
                if tasks:
                    redisSendTaskAdd(tasks[0])
                    return json.dumps(tasks[0])
        else:
            return json.dumps({'errorText': 'Empty task name'})

    @task_ajax_action
    def process_getUserLastOpenTask(self):
        import random

        task = PM_Task.objects.filter(
            closed=False,
            active=True,
            realDateStart__isnull=False,
            resp=self.currentUser.id,
            dateModify__lt=(datetime.datetime.now() - datetime.timedelta(minutes=1))
        ).exclude(
            status__code='ready'
        ).order_by('-critically', '-realDateStart')[:5]

        if task.count():
            taskTmp = task[random.randint(0, (task.count() - 1))]
            task = {
                'name': taskTmp.name,
                'url': taskTmp.url,
                'project__name': taskTmp.project.name
            }
            return json.dumps(task)
        else:
            return json.dumps({'user': self.currentUser.id})

    @task_ajax_action
    def process_insertBefore(self):
        taskId = self.getRequestData('id', FORMAT_TO_INTEGER)
        taskAfter = self.getRequestData('before_id', FORMAT_TO_INTEGER)

        if taskId:
            try:
                task = PM_Task.objects.get(pk=taskId)
            except PM_Task.DoesNotExist:
                return json.dumps({'error': 'task not found'})
            if not self.currentUser.get_profile().hasAccess(task, 'change'):
                return json.dumps({'error': 'access denied'})

            if taskAfter:
                try:
                    taskAfter = PM_Task.objects.get(pk=taskAfter)
                except PM_Task.DoesNotExist:
                    return json.dumps({'error': 'Parent task not found'})

                tasks = PM_Task.getForUser(self.currentUser, task.project,
                                           {
                                               'critically__gte': taskAfter.critically,
                                               'closed': False,
                                               'parentTask__isnull': True,
                                               'exclude': {'id': task.id},
                                               'project': task.project,  # even if manager, task can be moved within one project
                                           }, [], {'onlyParent': True})
                prevCritically = None
                taskSet = []
                secondTaskSet = []
                for eTask in tasks['tasks']:

                    if eTask.id == taskAfter.id:
                        if prevCritically and prevCritically > eTask.critically: #we just put cur task beyond two
                            if eTask.critically < task.critically < prevCritically: #if task was at the same place
                                return json.dumps({'result': 'task did not modified'})
                            else:
                                task.critically = (prevCritically + eTask.critically) / 2
                                task.save()
                                return json.dumps({'result': '1 task modified'})
                        elif prevCritically: #previous task exist
                            # secondTaskSet.append(task)
                            taskSet.reverse()
                            for uTask in taskSet:
                                secondTaskSet.append(uTask)
                                if prevCritically < uTask.critically:
                                    critPoint = (uTask.critically - prevCritically) / len(secondTaskSet)
                                    # i = 0
                                    for rTask in secondTaskSet:
                                        rTask.critically = prevCritically + critPoint
                                        rTask.save()

                                    task.critically = prevCritically + (critPoint / 2)
                                    task.save()
                                        # i += 1
                                    return json.dumps({'result': str(len(secondTaskSet) + 1) + ' tasks modified'})

                            #if all tasks before taskAfter have similar critically (but lesser that 1)
                            critPoint = (1 - prevCritically) / (len(secondTaskSet) + 1)
                            # i = 0
                            for rTask in secondTaskSet:
                                rTask.critically = prevCritically + critPoint
                                rTask.save()
                                # i += 1

                            task.critically = prevCritically + (critPoint / 2)
                            task.save()

                            return json.dumps({'result': str(len(secondTaskSet) + 1) + ' tasks modified - crit point: ' + str(critPoint)})
                        else:
                            task.critically = taskAfter.critically + 0.01
                            task.save()
                            return json.dumps({'result': '1 first task modified'})
                    else:
                        taskSet.append(eTask)

                    prevCritically = eTask.critically

                return json.dumps({'result': prevCritically})

    @task_ajax_action
    def process_appendTask(self):
        taskId = self.getRequestData('id', FORMAT_TO_INTEGER)
        taskParent = self.getRequestData('parent_id', FORMAT_TO_INTEGER)
        if taskId:
            try:
                task = PM_Task.objects.get(id=taskId)
                task.setParent(taskParent)
                if task.parentTask:
                    task.systemMessage(u'перенесена в расчет №' + str(task.parentTask.number))
                else:
                    task.systemMessage(u'перенесена в основной список ')
                return json.dumps({'result': 'ok'})
            except PM_Task.DoesNotExist:
                return json.dumps({'errorText': 'Task does not exist'})

    @task_ajax_action
    def process_deleteTask(self):
        taskId = self.getRequestData('id', FORMAT_TO_INTEGER)

        if taskId:
            try:
                task = PM_Task.objects.get(id=taskId)
                task.safeDelete()
                for st in task.subTasks.all():
                    st.safeDelete()
                return json.dumps({'result': 'ok', 'deleted': True})
            except PM_Task.DoesNotExist:
                return json.dumps({'errorText': 'Task does not exist'})


class TaskWidgetManager:
    def parseTaskCreateString(self, taskString):
        return {}

    @staticmethod
    def getUsersOfCurrentProject(project, aRoleCodes):
        from PManager.models import PM_ProjectRoles, PM_Role

        return User.objects.order_by('last_name').filter(
            is_active=True,
            pk__in=PM_ProjectRoles.objects.filter(
                role__in=PM_Role.objects.filter(code__in=aRoleCodes), project=project
            ).values('user__id')
        ).select_related('profile')

    @staticmethod
    def getUsersThatUserHaveAccess(user, project):
        from PManager.models import PM_Role, PM_ProjectRoles

        users = User.objects.order_by('last_name').filter(is_active=True)
        if project:
            if user.get_profile().isManager(project):
                users = users.filter(pk__in=PM_ProjectRoles.objects.filter(
                    project__in=user.get_profile().managedProjects.values('id')).values('user__id'))
            else:
                try:
                    users = users.filter(
                        pk__in=PM_ProjectRoles.objects.filter(project=project).values('user__id'))
                except PM_Role.DoesNotExist:
                    pass

        else:
            userProjects = user.get_profile().getProjects()
            users = users.filter(
                pk__in=PM_ProjectRoles.objects.filter(project__in=userProjects).values('user__id')
            )

        return users

    @staticmethod
    def getUsersThatCanBeResponsibleInThisProject(user, project):
        if project:
            res = TaskWidgetManager.getUsersOfCurrentProject(project, ['employee', 'manager', 'client', 'guest'])
        else:
            res = TaskWidgetManager.getUsersThatUserHaveAccess(user, None)

        return res.order_by('first_name')

    @staticmethod
    def getResponsibleList(user, project):
        return TaskWidgetManager.getUsersThatCanBeResponsibleInThisProject(user, project)

    def getProject(self, defaultProject):
        return defaultProject
