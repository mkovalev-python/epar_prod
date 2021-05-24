# -*- coding:utf-8 -*-
__author__ = 'Gvammer'
from PManager.models import PM_Task, PM_Timer, PM_Task_Message
from PManager.viewsExt.tasks import TaskWidgetManager
from PManager.viewsExt.tools import templateTools
from django import forms
import datetime
from django.utils import timezone

def widget(request, headerValues,a,b):
    class FilterForm(forms.Form):
        fromDate = forms.DateTimeField(required=False)
        toDate = forms.DateTimeField(required=False)
        aUserId = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            required=False,
            choices=[(user.id,' '.join([user.last_name,user.first_name]))
                     for user in TaskWidgetManager.getUsersThatUserHaveAccess(request.user, headerValues['CURRENT_PROJECT'])
            ])

    filterForm = FilterForm(
        data=request.GET
    )
    cur_user_access_projects = [v['id'] for v in request.user.get_profile().getProjects().values('id')]
    weeksDelta = 4

    dateStart = datetime.datetime.now() - datetime.timedelta(weeks=weeksDelta)
    dateEnd = None
    users_id = filterForm['aUserId'].value()
    if filterForm.is_valid() and users_id:
        users_id_tmp = []
        for uId in users_id:
            users_id_tmp.append(int(uId))
        users_id = users_id_tmp
        del users_id_tmp

        dateStart = templateTools.dateTime.convertToDateTime(filterForm['fromDate'].value()) if filterForm['fromDate'].value() else None
        dateEnd = templateTools.dateTime.convertToDateTime(filterForm['toDate'].value()) if filterForm['toDate'].value() else None
        if dateEnd:
            dateEnd += datetime.timedelta(days=1) #include all day of end of range

        if dateStart and not dateEnd:
            dateEnd = datetime.datetime.now()
    else:
        users_id = []

    allUsers = TaskWidgetManager.getUsersThatUserHaveAccess(request.user, headerValues['CURRENT_PROJECT'])
    users = allUsers.filter(pk__in=users_id)

    filterProject = int(request.GET.get('project', 0))
    if filterProject:
        cur_user_access_projects = [filterProject]

    for user in users:
        profile = user.get_profile()
        if profile.avatar:
            profile.avatar = str(profile.avatar).replace('PManager', '')
        setattr(user,'profile',profile)

        if not user.email and user.username.find('@'):
            setattr(user, 'email', user.username)

        # query = 'SELECT SUM(`seconds`) as summ, id, user_id, task_id, dateStart, dateEnd from PManager_pm_timer' + \
        #         ' WHERE `user_id`=' + str(int(user.id)) + \
        #         ' AND `dateStart` > \'' + str(dateStart) + '\'' + \
        #         ((' AND `dateStart` < \'' + str(dateEnd) + '\'') if dateEnd else '') + \
        #         ' GROUP BY `task_id` ORDER BY `dateStart` DESC'
        # timers = PM_Timer.objects.raw(query)
        timers = PM_Timer.objects.filter(dateEnd__gt=dateStart, user=user)
        if dateEnd:
            timers = timers.filter(dateEnd__lt=dateEnd)

        arTaskTime = []
        allUserTime = 0
        allCommentsQty = 0
        allFilesQty = 0
        for timer in timers:
            try:
                task = timer.task
                if task.project.id not in cur_user_access_projects:
                    continue

                comments = PM_Task_Message.objects.filter(task=task, author=user)

                if dateEnd:
                    comments = comments.filter(dateCreate__lt=dateEnd)

                if dateStart:
                    comments = comments.filter(dateCreate__gt=dateStart)

                if timer.seconds:
                    allUserTime += int(timer.seconds)

                allCommentsQty += comments.count()
                arTaskTime.append({
                    'comments_qty': comments.count(),
                    'task': task,
                    'timer': timer,
                    'date': timer.dateEnd
                })

            except PM_Task.DoesNotExist:
                pass

        setattr(user, 'taskTime', arTaskTime)
        setattr(user, 'allTime', PM_Timer(seconds=allUserTime) if allUserTime else None)
        setattr(user, 'all_comments_qty', allCommentsQty)
        setattr(user, 'all_files_qty', allFilesQty)

        closedTaskQty = PM_Task.objects.filter(resp=user, active=True)
        commentsQty = PM_Task_Message.objects.filter(author=user)
        if dateEnd:
            closedTaskQty = closedTaskQty.filter(dateClose__lt=dateEnd)
            commentsQty = commentsQty.filter(dateCreate__lt=dateEnd)

        if dateStart:
            closedTaskQty = closedTaskQty.filter(dateClose__gt=dateStart)
            commentsQty = commentsQty.filter(dateCreate__gt=dateStart)

        closedTaskQty = closedTaskQty.count()
        commentsQty = commentsQty.count()

        setattr(user, 'closedTaskQty', closedTaskQty)
        setattr(user, 'commentsQty', commentsQty)

    return {
        'users': users,
        'allUsers': allUsers,
        'filterForm': filterForm,
        'now': templateTools.dateTime.convertToSite(timezone.make_aware(datetime.datetime.now(), timezone.get_current_timezone())),
        'week_ago': templateTools.dateTime.convertToSite(timezone.make_aware(datetime.datetime.now(), timezone.get_current_timezone()) - datetime.timedelta(days=7)),
        'title': u'Статистика пользователей'
    }