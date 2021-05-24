# -*- coding:utf-8 -*-
__author__ = 'Gvammer'
from PManager.models import PM_Project, PM_Task, PM_Milestone
from django import forms
from django.db.models import Count
from django.template import RequestContext
from django.core.context_processors import csrf


class ProjectForm(forms.ModelForm):
    class Meta:
        model = PM_Project
        fields = ["name", "description", "image", "author", "tracker"]


def widget(request, headerValues, ar, qargs):
    if request.user.is_staff:
        SET_USER_ROLE = 'manager'
        c = RequestContext(request, processors=[csrf])
        post = request.POST
        get = request.GET
        projectData = {}
        pform = {}
        is_new = True
        old_repository = False

        if 'id' in get:
            try:
                projectData = PM_Project.objects.get(id=int(get['id']), locked=False)
                if not request.user.get_profile().isManager(projectData):
                    return {'redirect': '/?error=Нет прав для редактирования проекта'}

                old_repository = projectData.repository
                pform = ProjectForm(instance=projectData)
                is_new = False
            except PM_Project.DoesNotExist:
                pass
        else:
            pform = ProjectForm(data=post) # A form bound to the POST data
            projectData = post

        if request.method == 'POST':
            post.update({'author': request.user.id})
            post.update({'tracker': 1})

            pform = ProjectForm(
                instance=projectData if hasattr(projectData, 'id') else None,
                data=post,
                files=request.FILES
            )

            # pform.data = post
            # pform.files = request.FILES
            if pform.is_valid():
                instance = pform.save()

                settings = {}
                for k, v in request.POST.iteritems():
                    if k.find('settings_') > -1:
                        k = k.replace('settings_', '')
                        settings[k] = v

                instance.setSettings(settings)
                instance.save()

                if is_new:
                    request.user.get_profile().setRole(SET_USER_ROLE, instance)
                    if request.POST.get('template'):
                        pId = int(request.POST.get('template'))
                        try:
                            p = PM_Project.objects.get(pk=pId)
                            instance.settings = p.settings
                            instance.save()

                            parentTasks = {}
                            parentTasksOfParentTasks = {}
                            milestones = {}
                            for milestone in p.milestones.all():
                                m = PM_Milestone(
                                    name=milestone.name,
                                    project=instance
                                )
                                m.save()
                                milestones[milestone.id] = m

                            for task in p.projectTasks.annotate(
                                    children_cnt=Count('subTasks')).filter(active=True, children_cnt__gt=0):
                                t = PM_Task(
                                    name=task.name,
                                    text=task.text,
                                    project=instance,
                                    author=request.user
                                )

                                if task.milestone:
                                    t.milestone = milestones[task.milestone.id]

                                t.save()

                                parentTasks[task.id] = t

                                if task.parentTask:
                                    parentTasksOfParentTasks[task.id] = task.parentTask.id

                            for taskIdOld, taskNew in parentTasks.iteritems():
                                if parentTasksOfParentTasks.get(taskIdOld):
                                    taskNew.parentTask = parentTasks[parentTasksOfParentTasks.get(taskIdOld)]
                                    taskNew.save()

                            for task in p.projectTasks.annotate(
                                    children_cnt=Count('subTasks')).filter(active=True, children_cnt=0):
                                t = PM_Task(
                                    name=task.name,
                                    text=task.text,
                                    project=instance,
                                    author=request.user
                                )

                                if task.milestone:
                                    t.milestone = milestones[task.milestone.id]

                                if task.parentTask:
                                    t.parentTask = parentTasks.get(task.parentTask.id)

                                t.save()

                        except PM_Project.DoesNotExist:
                            pass

                    return {'redirect': '/?project=' + str(instance.id)}

                return {'redirect': request.get_full_path()}
            else:
                pass
        return {
            'projectData': projectData,
            'title': u'Добавление проекта',
            'form': pform,
            'is_new': is_new,
            'templates': PM_Project.objects.filter(description='template'),
            'settings': projectData.getSettings() if projectData and
                            hasattr(projectData, 'settings') and
                            projectData.settings else {}
        }

    else:
       return {'redirect': '/payment/'}