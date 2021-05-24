# -*- coding:utf-8 -*-
__author__ = 'Tonakai'
from PManager.models.tasks import PM_Task, ObjectTags, PM_Task_Message
from django.db.models import Count


def similar_tasks(task_id, limit=4, tagsRelations=[]):
    aSimilarTasks = []
    try:
        task = PM_Task.objects.get(pk=int(task_id))
    except (PM_Task.DoesNotExist, ValueError, TypeError):
        return aSimilarTasks

    aSimilarTasks = task.getSimilar(task.name + (task.text or ''), task.project)[:limit]
    aSimilar = []
    for t in aSimilarTasks:
        if t.id != task.id:
            aSimilar.append(t)

    return aSimilar


def tags_relations(task):
    tags = task.tags.all()
    return ObjectTags.objects.filter(tag__in=tags.values_list('tag', flat=True))\
        .annotate(dcount=Count('object_id')) if tags else []


def similar_solutions(task_id, limit=4):
    tasks = similar_tasks(task_id, limit)
    tasks_ids = set(task.id for task in tasks)
    a_messages = []
    try:
        messages = PM_Task_Message.objects.filter(task__in=tasks_ids, solution=True)
        for message in messages:
            a_messages.append(message)
        return a_messages
    except PM_Task_Message.DoesNotExist:
        return a_messages


