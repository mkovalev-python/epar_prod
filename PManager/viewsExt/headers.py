# -*- coding:utf-8 -*-
__author__ = 'Gvammer'
from PManager.models import PM_Project, PM_ProjectRoles
from PManager.viewsExt.forms import WhoAreYou, sendFeedBackEmail
from django.contrib.auth import logout
from PManager.services.trackers import get_tracker
from django.http import Http404

TRACKER = get_tracker(1)


def set_project_in_session(project_id, projects, request):
    '''
    This function sets a project from id, and stores it in a session
    so that next requests will have access to it
    '''
    project = None
    if project_id == 0 or project_id not in projects:
        request.COOKIES["CURRENT_PROJECT"] = 0
        return project
    try:
        project = PM_Project.objects.get(closed=False, id=int(project_id))
        request.COOKIES["CURRENT_PROJECT"] = project.id
    except (PM_Project.DoesNotExist, ValueError):
        request.COOKIES["CURRENT_PROJECT"] = 0
    return project


def get_project_in_session(projects, request):
    '''
    This function gets a stored project from session data
    '''
    project = None
    project_id = request.COOKIES.get("CURRENT_PROJECT", 0)
    try:
        project_id = int(project_id)
        if project_id in projects:
            project = PM_Project.objects.get(pk=project_id)
            return project
        else:
            request.COOKIES["CURRENT_PROJECT"] = 0
    except PM_Project.DoesNotExist:
        request.COOKIES["CURRENT_PROJECT"] = 0
    except ValueError:
        request.COOKIES["CURRENT_PROJECT"] = 0
    return project


# SET_COOKIE - куки, которые необходимо поставить
# CURRENT_PROJECT - текущий выбранный проект в трекере
def initGlobals(request):
    SET_COOKIE = {}
    bIsAuthenticated = request.user.is_authenticated()
    if bIsAuthenticated:
        myProjects = request.user.get_profile().getProjects().values('id')
        # myProjects = list()
        projects = []
        for project in myProjects:
            projects.append(project['id'])
    else:
        projects = []

    redirect = False

    if 'project' in request.REQUEST:
        project_id = int(request.REQUEST.get('project', 0))
        CURRENT_PROJECT = set_project_in_session(
            project_id,
            projects,
            request)
        SET_COOKIE["CURRENT_PROJECT"] = request.COOKIES["CURRENT_PROJECT"]
        if CURRENT_PROJECT is None and project_id != 0:
            if not bIsAuthenticated:
                redirect = '/login/'
            else:
                redirect = '/404'
    else:
        CURRENT_PROJECT = get_project_in_session(projects, request)
        SET_COOKIE["CURRENT_PROJECT"] = request.COOKIES["CURRENT_PROJECT"]

    if not CURRENT_PROJECT and len(projects):
        redirect = '/?project=' + str(projects[0])

    if request.method == 'POST':
        form = WhoAreYou(request.POST)

        if form.is_valid():
            currentUser = request.user
            currentUser.first_name = form.cleaned_data['name']
            currentUser.last_name = form.cleaned_data['last_name']
            currentUser.set_password(form.cleaned_data['password'])
            currentUser.save()

            try:
                project = PM_Project.objects.get(author=currentUser)
                if form.cleaned_data['sitename']:
                    project.name = form.cleaned_data['sitename']
                    project.save()

                if form.cleaned_data['phone']:
                    prof = currentUser.get_profile()
                    prof.phoneNumber = form.cleaned_data['phone']
                    prof.save()

                if 'need_manager' not in form.cleaned_data or form.cleaned_data['need_manager'] == 'N':
                    pass
                else:
                    sendFeedBackEmail(
                        request.user.first_name + ' ' + request.user.last_name,
                        request.user.email,
                        'Нужен менеджер',
                        'Мне нужен менеджер (' + str(request.user.get_profile().phoneNumber or '') + ')'
                    )

                redirect = "/?project=" + str(project.id)
            except PM_Project.DoesNotExist:
                projects = currentUser.get_profile().getProjects()
                if projects:
                    redirect = "/?project=" + str(projects[0].id)
                else:
                    redirect = "/"

        WhoAreYouForm = False

    elif bIsAuthenticated and not request.user.last_name:
        WhoAreYouForm = WhoAreYou()
    else:
        WhoAreYouForm = False

    if 'logout' in request.GET and bIsAuthenticated:
        if request.GET['logout'] == 'Y':
            logout(request)
            redirect = "/"

    can_invite = False
    is_manager = False
    if CURRENT_PROJECT and bIsAuthenticated:
        can_invite = (request.user.id == CURRENT_PROJECT.author.id or
                      request.user.get_profile().isManager(CURRENT_PROJECT))
        is_manager = request.user.get_profile().isManager(CURRENT_PROJECT)

    is_author = bIsAuthenticated and request.user.createdProjects.exists()

    return {
        'SET_COOKIE': SET_COOKIE,
        'CURRENT_PROJECT': CURRENT_PROJECT,
        'CAN_INVITE': can_invite,
        'IS_MANAGER':  is_manager,
        'IS_AUTHOR':  is_author,
        'FIRST_STEP_FORM': WhoAreYouForm,
        'REDIRECT': redirect,
        'COOKIES': request.COOKIES
    }
