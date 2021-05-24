# -*- coding:utf-8 -*-
__author__ = 'Gvammer'
from django.shortcuts import HttpResponse
from django.template import loader, RequestContext
from django.contrib.auth.models import User
from PManager.viewsExt.tools import EmailMessage
from PManager.viewsExt.headers import initGlobals
from PManager.models.users import PM_User, Specialty
from PManager.models.tasks import PM_Task_Message
from PManager.viewsExt.tasks import TaskWidgetManager
from django.db.models import Q
from PManager.viewsExt import headers
import json

class userHandlers:
    @staticmethod
    def getResponsibleMenu(request):
        headerValues = headers.initGlobals(request)
        widget_manager = TaskWidgetManager()
        draft_id = request.GET.get('draft_id', None)
        if draft_id:
            from PManager.services.task_drafts import get_draft_by_id
            draft = get_draft_by_id(draft_id, request.user)
            if draft:
                users = draft.users.exclude(id=draft.author_id)
            else:
                users = dict()
        else:
            users = widget_manager.getResponsibleList(request.user, headerValues['CURRENT_PROJECT'])
        c = RequestContext(request, {
            'users': users
            })
        t = loader.get_template('helpers/responsible_menu.html')
        return HttpResponse(t.render(c))

    @staticmethod
    def getMyTeam(request):
        widgetManager = TaskWidgetManager()
        resps = widgetManager.getResponsibleList(request.user, None)
        if request.POST.get('q'):
            q = request.POST.get('q')
            resps = resps.filter(Q(Q(first_name__icontains=q) | Q(last_name__icontains=q)))

        aResps = []
        for resp in resps:
            p = resp.get_profile()
            respDict = {
                'first_name': resp.first_name,
                'last_name': resp.last_name,
                'rel': p.avatar_rel,
                'id': resp.id,
                'msg': PM_Task_Message.objects.filter(author=resp, userTo=request.user, read=False).count()
            }
            histasksQty = resp.todo.filter(active=True, closed=False).count()
            respDict['openTasksQty'] = histasksQty
            aResps.append(respDict)

        return HttpResponse(json.dumps(aResps))

    @staticmethod
    def setUserOptions(request):
        action = request.POST['action']
        if not request.user.is_authenticated():
            return HttpResponse('')

        curUser = request.user

        response = u''
        if action == 'setRole':
            userId = request.POST['user']
            projectId = int(request.REQUEST.get('roleProject', 0))
            if projectId:
                managedProjects = curUser.get_profile().managedProjects
                for p in managedProjects:
                    if projectId == p.id:
                        roleCode = request.POST.get('role', None)
                        set = int(request.POST.get('set', 0))
                        user = User.objects.get(pk=userId)
                        prof = user.get_profile()

                        if set:
                            prof.setRole(roleCode, p)
                        # else:
                        #     prof.deleteRole(roleCode, p)

                return HttpResponse('ok')

        elif action == 'inviteUser':
            arEmail = request.POST.getlist('email[]', {})

            if arEmail:
                for email in arEmail:
                    roles = request.POST.getlist('roles['+email+'][]', [])

                    if not EmailMessage.validate_email(email):
                        return HttpResponse(u'Email введен неверно')
                    if not roles:
                        return HttpResponse(u'Не введено ни одной роли')

                    headers = initGlobals(request)
                    p = headers['CURRENT_PROJECT']
                    if request.user.get_profile().isManager(p):
                        if p:
                            user = PM_User.getOrCreateByEmail(email, p, roles.pop())

                            for role in roles:
                                user.get_profile().setRole(p, role)

            return HttpResponse('ok')

        elif action == 'getUsers':
            return userHandlers.getMyTeam(request)

        elif action == 'addSpecialty':
            userId = request.POST['user']
            specialty = request.POST['specialty'].upper()
            user = User.objects.get(pk=userId)
            prof = user.get_profile()
            if specialty in prof.specialties.values_list('name', flat=True):
                return HttpResponse('already has this specialty')
            elif user == curUser or curUser.is_superuser:
                specialty, created = Specialty.objects.get_or_create(name=specialty)
                prof.specialties.add(specialty)
                prof.save()
                return HttpResponse(json.dumps({'id': specialty.id, 'name': specialty.name}))

        elif action == 'deleteSpecialty':
            userId = request.POST['user']
            specialty = request.POST['specialty']
            try:
                specialty = int(specialty)
            except ValueError:
                return HttpResponse('specialtyId expected')
            user = User.objects.get(pk=userId)
            prof = user.get_profile()
            if user == curUser or curUser.is_superuser:
                specialty = Specialty.objects.get(id=specialty)
                prof.specialties.remove(specialty)
                prof.save()
                return HttpResponse('specialty deleted')


class usersActions:
    def set_user_roles(self):
        pass