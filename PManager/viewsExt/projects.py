# -*- coding:utf-8 -*-
__author__ = 'Gvammer'
from django.shortcuts import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.http import Http404
from django.template import loader, RequestContext
from PManager.models import PM_Task, PM_Project, PM_Achievement, SlackIntegration
from PManager.models import PM_Project_Achievement, PM_ProjectRoles
from PManager.models import AccessInterface, Credit
from django import forms
from tracker.settings import COMISSION
from PManager.viewsExt.headers import set_project_in_session
import json, math


class InterfaceForm(forms.ModelForm):
    class Meta:
        model = AccessInterface
        fields = ["name", "address", "port", "protocol",
                  "username", "password", "access_roles", "project"]


def projectDetail(request, project_id):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/')

    project = get_object_or_404(PM_Project, id=project_id)
    profile = request.user.get_profile()

    if not profile.hasRole(project) or project.locked:
        raise Http404('Project not found')

    set_project_in_session(project.id, [project.id], request)
    aMessages = {
        'client': u'Бонусы за каждый час закрытых проектов списываются с клиента, у которого установлена ставка.',
        'manager': u'Менеджеры проектов видят все проекты и имеют возможность изменять настройки проекта.',
        'employee': u'Сотрудники видят только свои проекты и сметы, в которые их пригласили в качестве наблюдателей.',
        'guest': u'Гости могут видеть только проекты, в которых они назначены наблюдателями, в переписке гости видят только адресованные им сообщения.',
    }
    show = dict(manager=True)
    show['employee'] = profile.isManager(project) or profile.isEmployee(project)
    show['client'] = profile.isManager(project) or profile.isClient(project)
    show['guest'] = profile.isManager(project)

    needComission = profile.isManager(project) or profile.isClient(project)

    aDebts = Credit.getUsersDebt([project])
    oDebts = dict()
    for x in aDebts:
        oDebts[x['user_id']] = int(x['sum'])

    aRoles = dict()

    for role in PM_ProjectRoles.objects.filter(project=project, user__is_active=True):
        if not show[role.role.code]:
            continue

        if role.role.name not in aRoles:
            aRoles[role.role.name] = dict(role=role, users=[], text=aMessages[role.role.code])

        prof = role.user.get_profile()
        curUser = role.user

        rate = int(math.floor(role.rate or prof.sp_price or 0))
        if needComission:
            clientComission = int(project.getSettings().get('client_comission', 0) or COMISSION)
            rate = int(math.floor(rate * (clientComission + 100) / 100))

        setattr(curUser, 'rate', rate)
        setattr(curUser, 'payment_type', role.payment_type)
        # setattr(curUser, 'defaultRate', prof.sp_price)
        setattr(curUser, 'sum', oDebts.get(role.user.id, None))
        setattr(curUser, 'role_id', role.id)

        aRoles[role.role.name]['users'].append(curUser)

    bCurUserIsAuthor = request.user.id == project.author.id or profile.isManager(project)
    if bCurUserIsAuthor:
        action = request.POST.get('action', None)
        if action:
            role_id = request.POST.get('role')
            role = None
            responseObj = {}
            try:
                role = PM_ProjectRoles.objects.get(pk=role_id, project=project)
            except PM_ProjectRoles.DoesNotExist:
                responseObj = {'error': 'Something is wrong  :-('}

            if action == 'update_payment_type':
                if role:
                    type = 'real_time' if request.POST.get('value', '') == 'real_time' else 'plan_time'
                    role.payment_type = type
                    role.save()
                    responseObj = {'result': 'payment type updated'}

            elif action == 'update_rate':
                if role:
                    rate = int(request.POST.get('value', 0))
                    role.rate = rate
                    role.save()
                    responseObj = {'result': 'rate updated'}

            elif action == 'remove_role':
                if role:
                    res = role.safeDelete()
                    if res:
                        responseObj = {'result': 'role removed'}
                    else:
                        responseObj = {'error': u'Вы не можете удалить последнюю роль менеджера в проекте'}

            elif action == 'send_payment':
                if role:
                    sum = int(request.POST.get('sum', 0))
                    comment = request.POST.get('comment', '')
                    p = Credit(user=role.user, project=project, value=sum, type='payment', comment=comment)
                    p.save()

                    responseObj = {'result': 'payment added'}

            elif action == 'change_name':
                if 'name' in request.POST:
                    project.name = request.POST['name']
                elif 'description' in request.POST:
                    project.description = request.POST['description']
                elif 'file' in request.FILES:
                    project.image = request.FILES['file']

                project.save()

                responseObj = {'result': 'ok'}

            elif action == 'upload_project_avatar':
                image = request.FILES.get('image')
                project.image = image
                project.save()
                responseObj = {'path': project.image.url}

            elif action == 'update_achievement_exist':
                if 'achievement' in request.POST:
                    try:
                        ac = PM_Achievement.objects.get(pk=int(request.POST['achievement']))
                        exist = int(request.POST.get('value', False))
                        if exist:
                            PM_Project_Achievement.get_or_create(achievement=ac, project=project)
                        else:
                            pac = PM_Project_Achievement.objects.filter(achievement=ac, project=project)
                            pac.delete()

                        responseObj = {'result': 'ok'}
                    except PM_Achievement.DoesNotExist, PM_Project_Achievement.DoesNotExist:
                        responseObj = {'error': 'Achievement does not exist'}

            elif action == 'update_achievement_value':
                if 'achievement' in request.POST:
                    try:
                        ac = PM_Achievement.objects.get(pk=int(request.POST['achievement']))

                        pac, created = PM_Project_Achievement.get_or_create(achievement=ac, project=project)
                        pac.value = int(request.POST.get('value', 0))
                        pac.save()

                        responseObj = {'result': 'ok'}
                    except PM_Achievement.DoesNotExist:
                        responseObj = {'error': 'Achievement does not exist'}

            elif action == 'update_achievement_type':
                if 'achievement' in request.POST:
                    try:
                        ac = PM_Achievement.objects.get(pk=int(request.POST['achievement']))

                        pac, created = PM_Project_Achievement.get_or_create(achievement=ac, project=project)
                        pac.type = request.POST.get('value', 'fix')
                        pac.save()

                        responseObj = {'result': 'ok'}
                    except PM_Achievement.DoesNotExist:
                        responseObj = {'error': 'Achievement does not exist'}

            return HttpResponse(json.dumps(responseObj))

    canDeleteInterface = profile.isManager(project)
    canDeleteProject = request.user.is_superuser or request.user.id == project.author.id
    canEditProject = request.user.is_superuser or request.user.id == project.author.id

    try:
        s = SlackIntegration.objects.get(project=project)
        setattr(project, 'slackUrl', s.url)
    except SlackIntegration.DoesNotExist:
        setattr(project, 'slackUrl', '')

    if 'settings_save' in request.POST and request.POST['settings_save'] and canEditProject:
        if 'is_closed' in request.POST \
                and (bool(request.POST['is_closed']) != project.closed)\
                and canDeleteProject:
            project.closed = bool(request.POST['is_closed'])

        parseSettingsFromPost(project, request)
        project.save()
        return HttpResponseRedirect(request.path)


    if 'integration_settings_save' in request.POST and request.POST['integration_settings_save'] and canEditProject:
        if 'repository' in request.POST and request.POST['repository'] != project.repository:
            project.repository = request.POST['repository']

        parseSettingsFromPost(project, request)
        project.save()
        return HttpResponseRedirect(request.path)

    if 'integration_messangers_settings_save' in request.POST \
            and request.POST['integration_messangers_settings_save'] and canEditProject:
        if 'slack_url' in request.POST and request.POST['slack_url'] != project.slackUrl:
            try:
                s = SlackIntegration.objects.get(project=project)
            except SlackIntegration.DoesNotExist:
                s = SlackIntegration(project=project)

            s.url = request.POST['slack_url']
            s.save()
            setattr(project, 'slackUrl', s.url)

        return HttpResponseRedirect(request.path)

    interfaces = AccessInterface.objects.filter(project=project)
    interfaces_html = ''
    t = loader.get_template('details/interface.html')
    for interface in interfaces:
        c = RequestContext(request, {
            'interface': interface,
            'canDelete': canDeleteInterface,
        })

        interfaces_html += t.render(c)

    achievements = PM_Achievement.objects.filter(use_in_projects=True)
    ar_achievements = []
    ar_project_achievements = {}
    for p_ac in PM_Project_Achievement.objects.filter(project=project).select_related('achievement'):
        ar_project_achievements[p_ac.achievement.id] = p_ac

    for achievement in achievements:
        if achievement.id in ar_project_achievements:
            setattr(achievement, 'project_relation', ar_project_achievements[achievement.id])

        ar_achievements.append(achievement)

    projectSettings = project.getSettings()
    c = RequestContext(request, {
        'project': project,
        'pageTitle': project.name,
        'roles': aRoles,
        'form': InterfaceForm(),
        'interfaces': interfaces_html,
        'canDelete': canDeleteProject,
        'canEdit': canEditProject,
        'bCurUserIsAuthor': bCurUserIsAuthor,
        'messages': aMessages,
        'settings': projectSettings,
        'achievements': ar_achievements,
        'colors': [(code, projectSettings.get('color_name_'+code, '')) for code, color in PM_Task.colors]
    })

    t = loader.get_template('details/project.html')
    return HttpResponse(t.render(c))


def parseSettingsFromPost(project, request):
        settings = project.getSettings()

        for k, v in request.POST.iteritems():
            if k.find('settings_') > -1:
                k = k.replace('settings_', '')
                settings[k] = False if v == 'N' else v

        project.setSettings(settings)


def addInterface(request):
    post = request.POST
    try:
        project_id = int(post['pid'])
        project = PM_Project.objects.get(id=project_id)
        if request.user.get_profile().hasRole(project):
            post['project'] = project.id
            form = InterfaceForm(data=post)
            if form.is_valid():
                instance = form.save()
                return render(request, 'details/interface.html', {
                    'interface': instance
                })
    except PM_Project.DoesNotExist:
        pass

    return HttpResponse('Invalid form')


def removeInterface(request):
    interface = get_object_or_404(AccessInterface, id=int(request.POST['id']))
    if request.user.get_profile().isManager(interface.project):
        interface.delete()

    return HttpResponse('ok')


def project_server_setup(request, project_id):
    if not project_id:
        raise Http404
    try:
        from PManager.services.docker import server_request
        project = PM_Project.objects.get(pk=project_id)
        server_request(project)
        return HttpResponse("OK")
    except (PM_Project.DoesNotExist, RuntimeError, AttributeError):
        raise Http404


def project_server_status(request, project_id):
    if not project_id:
        raise Http404
    try:
        from PManager.services.docker import server_status_request
        project = PM_Project.objects.get(pk=project_id)
        status = server_status_request(project)
        if status:
            return HttpResponse("OK")
        else:
            return HttpResponse("ERROR")
    except (PM_Project.DoesNotExist, RuntimeError, AttributeError):
        raise Http404
