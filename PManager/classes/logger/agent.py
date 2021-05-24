__author__ = 'Gvammer'
def projectsDailyLog():
    return False

    from PManager.classes.logger.logger import Logger
    from PManager.models import LogData, PM_Task_Message, PM_Project, PM_Timer
    import datetime

    logger = Logger(modelClass=LogData)
    minDate = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
    maxDate = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
    today_range = (
                minDate,
                maxDate
            )
    for project in PM_Project.objects.filter(closed=False, locked=False):
        commentsQty = PM_Task_Message.objects.filter(
            dateCreate__range=today_range,
            project=project
        ).count()
        timers = PM_Timer.objects.raw(
                    'SELECT SUM(`seconds`) as summ, id, user_id from PManager_pm_timer' +
                    ' WHERE ' +
                    'task_id in ' +
                          '(SELECT id FROM PManager_pm_task WHERE `project_id`=' + str(int(project.id)) + ')' +
                    ' AND dateEnd < \'' + maxDate.strftime('%Y-%m-%d %H:%M:%S') + '\' AND dateEnd > \'' + minDate.strftime('%Y-%m-%d %H:%M:%S') + '\''
                )
        allQty = float(commentsQty)
        for timer in timers:
            if timer.summ:
                allQty += float("%.2f" % (float(timer.summ)/3600))
        allQty = int(round(allQty))
        if allQty > 0:
            logger.log(None, 'ACTIVITY', allQty, project.id)

def usersDailyLog():
    from PManager.classes.logger.logger import Logger
    from PManager.models import LogData, PM_Task_Message
    from django.contrib.auth.models import User
    import datetime

    logger = Logger(modelClass=LogData)
    today_range = (
                datetime.datetime.combine(datetime.date.today(), datetime.time.min),
                datetime.datetime.combine(datetime.date.today(), datetime.time.max)
            )
    for user in User.objects.filter(is_active=True):
        commentsQty = PM_Task_Message.objects.filter(
            dateCreate__range=today_range,
            author=user
        ).count()
        if commentsQty > 0:
            logger.log(user, 'DAILY_COMMENTS', commentsQty)
