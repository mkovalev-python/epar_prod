# -*- coding:utf-8 -*-
__author__ = 'Gvammer'
from PManager.viewsExt.tools import templateTools, taskExtensions
from PManager.models import PM_Task, PM_Files, ObjectTags, PM_User, PM_Task_Status, PM_MilestoneChanges, \
    PM_File_Category
import time, datetime
from django.contrib.auth.models import User
from django.db.models import Count
from PManager.viewsExt.tasks import TaskWidgetManager
from PManager.widgets.tasklist.widget import get_user_tag_sums, get_task_tag_rel_array
import json
from django.http import HttpResponse


def widget(request, headerValues, ar, qargs):
    widgetManager = TaskWidgetManager()
    post = request.POST
    deadline = post.get('deadline', time.strftime('%d.%m.%Y'))

    deadline = templateTools.dateTime.convertToDateTime(deadline)
    name = post.get('name', False)
    status = post.get('status', False)
    if status:
        status = PM_Task_Status.objects.get(code=status)

    if request.GET.get('id', False):
        task = PM_Task.objects.get(id=int(request.GET.get('id', False)))
    else:
        task = False

    userTagSums = {}

    if name:
        planTime = post.get('planTime', 0)
        planTimeMainOrg = post.get('planTimeMainOrg', 0)
        planTimeRegulator = post.get('planTimeRegulator', 0)

        uploaded_files = post.getlist('files') if 'files' in post else []
        uploaded_files_ro = post.getlist('filesro') if 'filesro' in post else []
        uploaded_files_eo = post.getlist('fileseo') if 'fileseo' in post else []

        if planTime:
            planTime = planTime.replace(',', '.')
            if task and task.milestone:
                oldPlanTime = task.planTime or 0
                change = PM_MilestoneChanges(milestone=task.milestone, value=float(planTime)-oldPlanTime)
                change.save()

        arSaveFields = {
            'name': name,
            'text': post.get('description', ''),
            'text_ro': post.get('description_ro', ''),
            'text_eo': post.get('description_eo', ''),
            'repeatEvery': post.get('repeatEvery', 0),
            'deadline': deadline,
            'critically': float(post.get('critically', 0)) if post.get('critically', 0) else 0.5,
            'hardness': float(post.get('hardness', 0)) if post.get('hardness', 0) else 0.5,
            'project_knowledge': float(post.get('project_knowledge', 0)) if post.get('project_knowledge', 0) else 0.5,
            'reconcilement': float(post.get('reconcilement', 0)) if post.get('reconcilement', 0) else 0.5,
            'planTime': float(planTime.replace(',', '.')),
            'planTimeMainOrg': float(planTimeMainOrg.replace(',', '.')),
            'planTimeRegulator': float(planTimeRegulator.replace(',', '.')),
            'status': status if status else task.status
        }
        if task:
            for k, val in arSaveFields.iteritems(): setattr(task, k, val)
        else:
            arSaveFields['author'] = request.user
            task = PM_Task(**arSaveFields)

        respId = post.get('resp', '')

        if str(respId).find('@') > -1:
            oUserProfile = PM_User.getOrCreateByEmail(respId, task.project, 'employee')
            respId = oUserProfile.id
        if respId:
            task.resp = User.objects.get(pk=int(respId))
            arSaveFields['resp'] = task.resp

        """Проверка и создание папки"""
        if not task.category_id:
            category = PM_File_Category(name=task.name)
            if task.parentTask:
                category.parent_id = task.parentTask.category_id
            category.save()
            category.projects.add(task.project_id)
            task.category = category
        if task.name != task.category.name:
            category_name = PM_File_Category.objects.get(id=task.category_id)
            category_name.name = task.name
            category_name.save()
        task.save()

        for filePost in uploaded_files:
            try:
                if not PM_Files.objects.filter(pk=filePost).exists():
                    continue
                if PM_Files.objects.get(pk=filePost).attach:
                    fileName = PM_Files.objects.get(pk=filePost).name
                    getAttachFile = PM_Files.objects.get(name=fileName, attach=False, double=False)
                    task.files.add(getAttachFile)
                    PM_Files.objects.get(name=fileName, attach=True, double=False).delete()
                else:
                    file_obj = PM_Files.objects.get(pk=filePost)
                    file_obj.category_id = task.category_id
                    file_obj.save()
                    task.files.add(file_obj)
            except PM_Files.DoesNotExist():
                pass

        for filePost in uploaded_files_ro:
            try:
                if not PM_Files.objects.filter(pk=filePost).exists():
                    continue
                if PM_Files.objects.get(pk=filePost).attach:
                    fileName = PM_Files.objects.get(pk=filePost).name
                    getAttachFile = PM_Files.objects.get(name=fileName, attach=False, double=False)
                    task.files_ro.add(getAttachFile)
                    PM_Files.objects.get(name=fileName, attach=True, double=False).delete()
                else:
                    file_obj = PM_Files.objects.get(pk=filePost)
                    file_obj.category_id = task.category_id
                    file_obj.save()
                    task.files_ro.add(file_obj)
            except PM_Files.DoesNotExist():
                pass

        for filePost in uploaded_files_eo:
            try:
                if not PM_Files.objects.filter(pk=filePost).exists():
                    continue
                if PM_Files.objects.get(pk=filePost).attach:
                    fileName = PM_Files.objects.get(pk=filePost).name
                    getAttachFile = PM_Files.objects.get(name=fileName, attach=False, double=False)
                    task.files_eo.add(getAttachFile)
                    PM_Files.objects.get(name=fileName, attach=True, double=False).delete()
                else:
                    file_obj = PM_Files.objects.get(pk=filePost)
                    file_obj.category_id = task.category_id
                    file_obj.save()
                    task.files_eo.add(file_obj)
            except PM_Files.DoesNotExist():
                pass

        aObservers = post.getlist('observers')
        for (counter, observer) in enumerate(aObservers):
            if observer.find('@') > -1:
                oUserProfile = PM_User.getOrCreateByEmail(observer, task.project, 'employee')
                aObservers[counter] = oUserProfile.id

        task.observers.clear()
        task.observers.add(*aObservers)
        task.saveTaskTags()

        if 'tags' not in arSaveFields:
            arSaveFields['tags'] = task.tags.all()
            
        arEmail = task.getUsersEmail([request.user.id])
        task.sendTaskEmail('task_changed', arEmail, 'Расчет изменен')

        backurl = request.GET.get('backurl', None)
        if backurl:
            return {'redirect': backurl}

    elif request.GET.get('id', False):
        from PManager.services.similar_tasks import tags_relations, similar_tasks
        arSaveFields = task
        if arSaveFields:
            tagsRelations = tags_relations(arSaveFields)
            aSimilarTasks = similar_tasks(arSaveFields.id, tagsRelations=tagsRelations)
            resp = arSaveFields.resp
            tags = arSaveFields.tags.all()
            observers = arSaveFields.observers.all()
            aUsersHaveAccess = widgetManager.getResponsibleList(request.user, None).values_list('id', flat=True)
            currentRecommendedUser, userTagSums = get_user_tag_sums(get_task_tag_rel_array(task), None, aUsersHaveAccess)
            arSaveFields = arSaveFields.__dict__
            arSaveFields.update({
                'tags': tags,
                'resp': resp,
                'observers': observers,
                'critically': arSaveFields.get('critically', 0.5),
                'hardness': arSaveFields.get('hardness', 0.5),
                'project_knowledge': arSaveFields.get('project_knowledge', 0.5),
                'reconcilement': arSaveFields.get('reconcilement', 0.5),
                'similarTasks': aSimilarTasks,
                'tagsRelations': tagsRelations,
                'files': task.files.all(),
                'files_ro': task.files_ro.all(),
                'files_eo': task.files_eo.all(),
                'status': status if status else task.status
            })

    else:
        arSaveFields = {}

    users = widgetManager.getResponsibleList(request.user, headerValues['CURRENT_PROJECT'])

    for field, val in arSaveFields.iteritems():
        if isinstance(val, datetime.datetime):
            arSaveFields[field] = val.strftime('%d.%m.%Y %H:%M')

    return {
        'id': request.GET.get('id', False),
        'post': arSaveFields,
        'project': task.project if task and task.project else headerValues['CURRENT_PROJECT'],
        'users': users,
        'recommendedUsers': [i for i, c in userTagSums.iteritems()],
        'title': u'Изменение задачи',
        'files': taskExtensions.getFileList(task.files.all()),
        'files_ro': taskExtensions.getFileList(task.files_ro.all()),
        'files_eo': taskExtensions.getFileList(task.files_eo.all()),
    }