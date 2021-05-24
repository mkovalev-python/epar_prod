# -*- coding:utf-8 -*-
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.formats import localize
from django.utils.timezone import now, localtime
from django.views.generic import FormView

from PManager.models import PM_Milestone, PM_Task, PM_Task_Message, PM_Files, PM_Project
from .forms import SupportForm


class BaseFormView(FormView):
    template_name = 'support_page/support_page_tpl.html'
    form_class = SupportForm

    def __init__(self, **kwargs):
        super(BaseFormView, self).__init__(**kwargs)
        self.hash = None
        self.milestone = None
        self.project = None
        self.author = None
        self.form_action_url = None

    def get_hash(self):
        self.hash = self.kwargs.get('hash')

    def get_milestone(self):
        pass

    def get_project(self):
        pass

    def get_author(self):
        pass

    def get_form_url(self):
        pass

    def dispatch(self, request, *args, **kwargs):
        self.get_form_url()
        return super(BaseFormView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(BaseFormView, self).get_context_data(**kwargs)
        context['form_action_url'] = self.form_action_url
        return context

    def get_success_url(self):
        return self.form_action_url

    def add_task(self, data):
        task = PM_Task(
            project=self.project,
            milestone=self.milestone,
            name=u'Новое обращение от {}'.format(localize(localtime(now()),  use_l10n=True)),
            author=self.author,
            text=u'Ссылка: {}.\n Как это работает: {}.\n Как должно работать: {}.\n Дополнительно: {}'.format(
                data['link'],
                data['work_actual'],
                data['work_should'],
                data['details'],
            ),
        )
        if data['priority']:
            task.critically = 0.99
        task.save()
        # save file
        if data['screenshot']:
            f = PM_Files(projectId=self.project, file=self.request.FILES['screenshot'])
            f.save()
            task.files.add(f)
        # add hidden message
        PM_Task_Message.objects.create(
            project=self.project,
            task=task,
            hidden=True,
            userTo=self.author,
            text=u'Имя: {}\n телефон: {}'.format(data['name'], data['phone'])
        )
        messages.success(self.request, u'Обращение успешно отправлено')

    def form_valid(self, form):
        self.get_hash()
        self.get_milestone()
        self.get_project()
        self.get_author()
        if self.project:
            self.add_task(form.cleaned_data)
        return HttpResponse('success')


class MilestoneFormView(BaseFormView):
    def get_form_url(self):
        self.form_action_url = reverse('support_page:milestone-form', kwargs=self.kwargs)

    def get_milestone(self):
        try:
            self.milestone = PM_Milestone.objects.get(id_md5=self.hash, closed=False)
        except PM_Milestone.DoesNotExist:
            messages.error(self.request, u'Неправильный URL. Обратитесь к менеджеру.')
            return HttpResponseRedirect(self.get_success_url())

    def get_project(self):
        self.project = self.milestone.project

    def get_author(self):
        self.author = self.milestone.manager


class ProjectFormView(BaseFormView):
    def get_form_url(self):
        self.form_action_url = reverse('support_page:project-form', kwargs=self.kwargs)

    def get_project(self):
        try:
            self.project = PM_Project.objects.get(id_md5=self.hash, closed=False)
        except PM_Project.DoesNotExist:
            messages.error(self.request, u'Неправильный URL. Обратитесь к менеджеру.')
            return HttpResponseRedirect(self.get_success_url())

    def get_author(self):
        self.author = self.project.author
