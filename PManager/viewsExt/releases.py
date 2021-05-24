# -*- coding:utf-8 -*-
__author__ = 'Gvammer'
from django.shortcuts import HttpResponse, render, HttpResponseRedirect
from PManager.models import PM_Milestone, PM_Project, PM_Task, Release
from django.template import RequestContext
from PManager.viewsExt.tools import templateTools
from PManager.viewsExt import headers


def releasesResponder(request, activeMenuItem=None):
    from PManager.viewsExt import headers

    headerValues = headers.initGlobals(request)
    user = request.user
    if not user.is_authenticated():
        return HttpResponseRedirect('/')

    if 'action' in request.POST:
        action = request.POST.get('action')
        if action == 'remove':
            id = request.POST.get('id', -1)

            release = Release.objects.get(pk=id)

            if user.get_profile().isManager(release.project):
                release.active = False
                release.save()
                return HttpResponse('ok')


    mprojects = []
    try:
        mprojects = [headerValues["CURRENT_PROJECT"]]
    except Exception:
        pass

    for project in mprojects:
        setattr(project, 'releaseList', project.releases.filter(active=True).order_by('-date'))

    return render(request, 'releases/index.html', {'projects': mprojects, 'pageTitle': u'Версии', 'activeMenuItem': 'releases'})