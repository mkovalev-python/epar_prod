# -*- coding:utf-8 -*-
__author__ = 'Gvammer'
from django.shortcuts import HttpResponse, render, HttpResponseRedirect
from django.utils.timezone import now
from django.views.generic import TemplateView

from PManager.models import PM_Milestone, PM_Project, PM_Task, PM_MilestoneChanges, PM_MilestoneDevPaymentApproval
from django.template import RequestContext
from PManager.viewsExt.tools import templateTools
from PManager.viewsExt import headers
from PManager.widgets.gantt.widget import create_milestone_from_post
from common.views.base_views import CustomLoginRequiredMixin


class ajaxMilestoneManager:
    def __init__(self, request):
        self.request = request

    def getRequestValue(self, key):
        if key in self.request.POST:
            return self.request.POST[key]
        else:
            return None


def milestoneForm(request):
    return render(request, 'helpers/milestone_create.html', dict())


def ajaxMilestonesResponder(request):
    milestone = None
    responseText = 'bad query'
    name = request.POST.get('name', '')
    user = request.user
    responsible_id = request.POST.get('responsible', 0)
    date = templateTools.dateTime.convertToDateTime(request.POST.get('date', ''))
    id = request.POST.get('id', None)
    task_id = int(request.POST.get('task_id', 0))
    critically = request.POST.get('critically', 2)
    action = request.POST.get('action', None)
    if not user.is_authenticated():
        return HttpResponse('Not authorized')

    project = None
    try:
        project = PM_Project.objects.get(
            pk=int(request.POST.get('project', 0)),
            closed=False,
            locked=False
        )
    except PM_Project.DoesNotExist:
        if id:
            try:
                milestone = PM_Milestone.objects.get(pk=id)
                project = milestone.project
            except PM_Milestone.DoesNotExist:
                project = None

    if action == 'remove':
        if id:
            try:
                milestone = PM_Milestone.objects.get(pk=id)
                status = milestone.close_milestone(now(), user)
                if status['is_closed']:
                    responseText = 'removed'
                else:
                    responseText = status['message']
            except PM_Milestone.DoesNotExist:
                responseText = 'Ошибка закрытия спринта. Группа расчетов не найден.'

    elif action == 'add_task_to_milestone':
        milestone = None
        if id:
            milestone = PM_Milestone.objects.get(pk=id)

        task = PM_Task.objects.get(pk=task_id)
        if task.milestone:
            change = PM_MilestoneChanges(milestone=task.milestone, value=-(task.planTime or 0))
            change.save()

        task.milestone = milestone
        task.save()

        if milestone:
            change = PM_MilestoneChanges(milestone=milestone, value=(task.planTime or 0))
            change.save()

        responseText = 'added'

    elif name and project:
        if not user.get_profile().isManager(project):
            return HttpResponse('user is not manager of project')

        if not milestone:
            milestone = None
        if id:
            try:
                milestone = PM_Milestone.objects.get(pk=id)
                milestone.name = name
                milestone.date = date
                milestone.project = project
            except PM_Milestone.DoesNotExist:
                pass
        else:
            milestone = PM_Milestone(name=name, date=date, project=project)

        if milestone:
            milestone.save()
            if responsible_id:
                milestone.responsible.clear()
                milestone.responsible.add(responsible_id)
            else:
                milestone.responsible.add(user)
            responseText = 'saved'

    return HttpResponse(responseText)


def milestonesResponder(request, activeMenuItem=None):
    from PManager.viewsExt import headers

    headerValues = headers.initGlobals(request)
    create_milestone_from_post(request, headerValues)
    user = request.user
    if not user.is_authenticated():
        return HttpResponseRedirect('/')

    cur_project = PM_Project.objects.get(pk=request.GET.get('project')) if request.GET.get('project', False) else None
    context = RequestContext(request)
    selected_project = context.get("CURRENT_PROJECT")
    if selected_project:
        mprojects = (selected_project,)
    else:
        mprojects = PM_Project.objects.filter(closed=False, locked=False)

    if cur_project:
        mprojects = mprojects.filter(pk=cur_project.id)

    return render(request, 'milestones/index.html', {'m_projects': mprojects, 'pageTitle': u'Цели',
                                                     'activeMenuItem': activeMenuItem,
                                                     'cur_project': cur_project})


def milestonesReportResponder(request, activeMenuItem=None):
    from PManager.viewsExt import headers

    header_values = headers.initGlobals(request)
    create_milestone_from_post(request, header_values)

    user = request.user
    if not user.is_authenticated():
        return HttpResponseRedirect('/')

    if request.GET.get('project', False):
        cur_project = PM_Project.objects.get(pk=request.GET.get('project'))
    else:
        cur_project = None

    context = RequestContext(request)
    selected_project = context.get("CURRENT_PROJECT")

    if selected_project:
        mprojects = (selected_project,)
    else:
        mprojects = PM_Project.objects.filter(closed=False, locked=False)

    if cur_project:
        mprojects = mprojects.filter(pk=cur_project.id)

    context_data = {
        'm_projects': mprojects,
        'pageTitle': u'Цели',
        'activeMenuItem': activeMenuItem,
        'cur_project': cur_project
    }

    return render(request, 'milestones/report.html', **context_data)


def milestones_close_confirmation(request, hash):
    milestone = PM_Milestone.objects.get(id_md5=hash, closed=True)
    milestone.milestone_close_confirmed(user=milestone.project.payer)
    return render(request, 'milestones/close_confirmed.html')


class BaseDeveloperMilestoneCreditApprove(CustomLoginRequiredMixin, TemplateView):
    template_name = 'milestones/dev_credit_approve.html'
    is_approved = None

    def add_approve(self, milestone_id):
        approve_status = PM_MilestoneDevPaymentApproval.objects.get(milestone_id=milestone_id, user=self.request.user)
        approve_status.is_approved = self.is_approved
        approve_status.save()

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['is_approved'] = self.is_approved
        self.add_approve(kwargs['id'])
        return self.render_to_response(context)


class DeveloperMilestoneCreditApprove(BaseDeveloperMilestoneCreditApprove):
    is_approved = True


class DeveloperMilestoneCreditNotApprove(BaseDeveloperMilestoneCreditApprove):
    is_approved = False
