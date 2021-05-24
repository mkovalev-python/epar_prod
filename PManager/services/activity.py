__author__ = 'rayleigh'
from PManager.models.tasks import PM_Task, PM_Task_Message, PM_Tracker, PM_Project


def last_project_activity(project):
    if project is None:
        return None
    try:
        message_last = PM_Task_Message.objects.filter(project=project).latest("dateCreate")
        return message_last.dateCreate
    except PM_Task_Message.DoesNotExist:
        try:
            last_task = PM_Task.objects.filter(project=project).latest("dateModify")
            return last_task.dateModify
        except PM_Task.DoesNotExist:
            return project.dateCreate


def last_task_activity(task):
    try:
        message_last = PM_Task_Message.objects.filter(task=task).latest("dateCreate")
        return message_last.dateCreate
    except PM_Task_Message.DoesNotExist:
        return task.dateCreate


def user_active_tasks(user_id):
    try:
        tasks_cnt = PM_Task.objects.filter(resp__id=user_id, closed=False, status__code='revision').count()
        return tasks_cnt
    except PM_Task.DoesNotExist:
        return 0