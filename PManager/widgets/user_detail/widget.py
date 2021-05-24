# -*- coding:utf-8 -*-
__author__ = 'Gvammer'
from PManager.models import ObjectTags, PM_Milestone, Credit, PM_Task, PM_Task_Message, PM_Timer, PM_Role, PM_Project, \
    PM_User_Achievement, LogData, PM_User
from PManager.widgets.tasklist.widget import widget as taskList
from django.db.models import Q
from PManager.viewsExt.tools import templateTools
from PManager.viewsExt.specialty import matchSpecialtyWithTags
from django.contrib.auth.models import User
import datetime
from PManager.services.rating import get_user_quality
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Sum


def widget(request, headerValues, ar, qargs):
    get = request.GET
    post = request.POST
    user = {}
    if 'id' in get:
        try:
            user = User.objects.get(pk=int(get['id']))
            profile = user.get_profile()
            # setattr(profile, 'rating', int(profile.rating or 0))
            cur_prof = request.user.get_profile()
            if 'action' in post:
                # add this user to project
                if post['action'] == 'add_to_project':
                    project = post.get('project', None)
                    role = post.get('role', None)
                    if role and project:
                        try:
                            project = PM_Project.objects.get(id=project)
                            role = PM_Role.objects.get(id=role)
                            if cur_prof.isManager(project):
                                profile.setRole(role.code, project)
                                if role.code == 'employee':
                                    if cur_prof.is_outsource:
                                        from PManager.models.agreements import Agreement
                                        Agreement.objects.get_or_create(payer=project.payer, resp=cur_prof.user)

                                return {
                                    'redirect': u'/user_detail/?id=' + unicode(get['id'])
                                }

                        except PM_Project.DoesNotExist:
                            raise u'Project does not exist'
                        except PM_Role.DoesNotExist:
                            raise u'Role does not exist'

                elif post['action'] == 'delete_user':
                    if request.user.is_superuser or request.user.is_staff and not user.is_staff:
                        user.is_active = False
                        user.save()

                        return {
                            'redirect': u'/user_list/'
                        }
                    else:
                        raise Exception(u'Нет прав для удаления прльзователя')

            if profile.avatar:
                profile.avatar = str(profile.avatar).replace('PManager', '')
            # проекты, к которым пользователь имеет доступ
            currentUserAccessProjects = cur_prof.getProjects()
            currentUserManagedProjects = cur_prof.getProjects(only_managed=True)

            tasksResult = taskList(
                request,
                headerValues, {
                    'filter': {
                        'resp': user,
                        'closed': False,
                        'allProjects': True
                    }
                },
                [Q(Q(project__in=currentUserManagedProjects) | Q(author=request.user) | Q(resp=request.user))],
                {
                    'pageCount': 10
                }
            )

            # tasksObserverResult = taskList(
            #     request,
            #     headerValues, {
            #         'filter': {
            #             'observers': user,
            #             'closed': False,
            #             'allProjects': True
            #         }
            #     },
            #     [Q(Q(project__in=currentUserManagedProjects) | Q(author=request.user) | Q(resp=request.user))]
            # )

            taskSum = PM_Task.objects.filter(resp=user, closed=False, dateClose__isnull=True, active=True,
                                             project__in=currentUserAccessProjects).count()
            taskSumPerMonth = PM_Task.objects.filter(
                resp=user,
                active=True,
                dateClose__gt=(datetime.datetime.now() - datetime.timedelta(weeks=4)),
                project__in=currentUserAccessProjects
            ).count()

            rest, sum = 0, 0
            # sp_price = int(profile.sp_price) if profile.sp_price else 0
            arUserBets = []
            if user.id == request.user.id:
                projectsForPayment = currentUserAccessProjects
            else:
                projectsForPayment = currentUserManagedProjects

            userRoles = [role for role in user.userRoles.filter(project__in=currentUserAccessProjects)]

            paymentsAndCredits = []
            if projectsForPayment.exists():
                projectsForPaymentsId = []
                for project in projectsForPayment:
                    projectsForPaymentsId.append(project.id)

                    timers = PM_Timer.objects.raw(
                        'SELECT SUM(`seconds`) as summ, id, user_id from PManager_pm_timer' +
                        ' WHERE `user_id`=' + str(int(user.id)) +
                        ' AND task_id in ' +
                        '(SELECT id FROM PManager_pm_task WHERE `project_id`=' + str(int(project.id)) + ') LIMIT 30'
                    )

                    projectBet = profile.getBet(project)
                    projectHours = 0
                    for timer in timers:
                        if timer.summ:
                            sumHours = float("%.2f" % (float(timer.summ) / 3600))
                            sum += sumHours
                            projectHours += sumHours

                    projPrice = 0
                    for o in Credit.objects.raw(
                                                                                            'SELECT sum(CASE WHEN user_id=' + str(
                                                                                            user.id) + ' THEN value ELSE -value END) as summ, id, user_id, project_id from PManager_credit' +
                                                                            ' WHERE (`user_id`=' + str(
                                                                    int(user.id)) + ' or `payer_id`=' + str(
                                                    int(user.id)) + ')'
                                                                    ' AND `project_id`=' + str(int(project.id)) + ' LIMIT 30'
                    ):
                        projPrice += o.summ if o.summ else 0

                    rest += projPrice
                    curRole = None
                    for role in userRoles:
                        if role.project.id == project.id:
                            curRole = role

                    if curRole and projPrice:
                        arUserBets.append(
                            {
                                'project': project.name,
                                'price': projPrice,
                                'bet': projectBet,
                                'project_id': project.id,
                                'role_id': curRole.id
                            }
                        )

                pAc = Credit.objects.filter(Q(Q(user=user) | Q(payer=user)),
                                            project__in=projectsForPaymentsId).order_by('-date')[:30]
                for credit in pAc:
                    setattr(credit, 'value',
                            credit.value if credit.user and credit.user.id == user.id else -credit.value)
                    paymentsAndCredits.append(credit)

            setattr(profile, 'sp', {
                'summ': sum,
                'rest': rest
            })

            userTimes = PM_Timer.objects.filter(user=user.id, task__project__id__in=currentUserAccessProjects).order_by(
                '-id')[:20]

            userKeys = []

            taskTemplate = templateTools.get_task_template()

            for task in tasksResult['tasks']:
                task['name'] = '<b>' + task['project']['name'] + '</b>: ' + task['name']

            # for task in tasksObserverResult['tasks']:
            #     task['name'] = '<b>' + task['project']['name'] + '</b>: ' + task['name']
            userProjectsOpenQty = profile.getProjects().filter(closed=False).count()
            userProjectsClosedQty = profile.getProjects(False, False, False, True).filter(closed=True).count()

            userProjects = profile.getProjects().filter(pk__in=currentUserAccessProjects)
            for project in userProjects:
                aRoles = []
                lastRequired = False
                for role in userRoles:
                    if role.project.id == project.id:
                        aRoles.append(role.role.code)
                        if not lastRequired:
                            lastRequired = role.isLastRequiredRole()

                setattr(project, 'roles', aRoles)
                setattr(project, 'canEdit', cur_prof.isManager(project) and not lastRequired)

            now = datetime.date.today()
            week = [now]
            for i in range(7):
                now = now - datetime.timedelta(days=1)
                week.append(now)

            week = week[::-1]

            timeGraph = []
            arWeekDays = {
                1: u'Пн',
                2: u'Вт',
                3: u'Ср',
                4: u'Чт',
                5: u'Пт',
                6: u'Сб',
                7: u'Вс',
            }
            for date in week:
                time = LogData.objects.raw(
                    'SELECT SUM(`value`) as summ, id, user_id from PManager_logdata WHERE `user_id`=' + str(
                        int(user.id)) + '' +
                    ' AND DATE(datetime) = \'' + date.isoformat() + '\'' +
                    ' AND code = \'DAILY_TIME\''
                )

                allTime = 0
                for timer in time:
                    allTime += timer.summ if timer.summ else 0

                date_range = (
                    datetime.datetime.combine(date, datetime.time.min),
                    datetime.datetime.combine(date, datetime.time.max)
                )

                tasksClosed = LogData.objects.filter(code='DAILY_TASKS_CLOSED', user=user,
                                                     datetime__range=date_range).count()
                commits = PM_Task_Message.objects.filter(dateCreate__range=date_range, author=user,
                                                         code='GIT_COMMIT').count()
                timeGraph.append({
                    'date': arWeekDays.get(date.isoweekday(), u''),
                    'time': str(round(allTime / 3600, 2)).replace(',', '.'),
                    'commits': commits,
                    'tasksClosed': tasksClosed
                })

            tagWeight = {}
            s = []
            specialties = profile.specialties.all()
            if specialties:
                tags = matchSpecialtyWithTags(specialties.values_list('name', flat=True))
                tagsId = tags.keys()
                if len(tagsId) > 0:
                    quality = get_user_quality(tagsId, user.id)

                    if quality:
                        for tag in quality:
                            tagWeight[tags[tag]] = quality[tag]

                maxTagWeight = 0
                for sp in specialties:
                    if sp.name in tagWeight:
                        setattr(sp, 'weight', tagWeight[sp.name])
                        if maxTagWeight < tagWeight[sp.name]:
                            maxTagWeight = tagWeight[sp.name]

                    s.append(sp)

                for sp in s:
                    if sp.name in tagWeight:
                        if maxTagWeight and tagWeight[sp.name]:
                            setattr(sp, 'weightPercent', tagWeight[sp.name] * 100 / maxTagWeight)

            taskTagCoefficient = 0
            taskTagPosition = 0
            for obj1 in ObjectTags.objects.raw(
                                                    'SELECT SUM(`weight`) as weight_sum, `id` from PManager_objecttags WHERE object_id=' + str(
                                                    user.id) + ' AND content_type_id=' + str(
                                    ContentType.objects.get_for_model(User).id) + ''):
                for obj2 in ObjectTags.objects.raw(
                                                        'SELECT COUNT(v.w) as position, id FROM (SELECT SUM(`weight`) as w, `id`, `object_id` from PManager_objecttags WHERE content_type_id=' + str(
                                                        ContentType.objects.get_for_model(
                                                                User).id) + ' GROUP BY object_id HAVING w >= ' + str(
                                                obj1.weight_sum or 0) + ') as v'):
                    taskTagPosition = obj2.position + 1
                    break

                taskTagCoefficient += (obj1.weight_sum or 0)
                break

            allPlanClosed = user.todo.filter(
                    planTime__gt=0,
                    closed=True,
                    dateClose__gt=(datetime.datetime.now() - datetime.timedelta(weeks=4))
                ).aggregate(Sum('planTime'))['planTime__sum'] or 0

            velocity = allPlanClosed * 100 / (22 * (profile.hoursQtyPerDay or 6))
            if velocity > 100:
                velocity = 100

            bugsQty = PM_Task_Message.objects.filter(task__in=user.todo.all(), bug=True).count()
            allTasksClosed = user.todo.filter(closed=True).exclude(author=user).count()
            overdueTasks = user.todo.exclude(author=user).filter(active=True, closedInTime=False, closed=True).count()
            quality = allTasksClosed * 100 / (overdueTasks + (bugsQty or 1))
            if quality > 100:
                quality = 100

            active_sprints_ids = PM_Milestone.get_active_milestones_ids()
            draft_sprints_ids = PM_Milestone.get_draft_milestones_ids()
            closed_sprints_ids = PM_Milestone.get_closed_milestones_ids()

            tmp_tasks = PM_Task.objects.filter(milestone__in=active_sprints_ids, active=True, resp=user)
            tmp_tasks = tmp_tasks.order_by('resp__last_name', 'project__name', 'milestone__name')
            tmp_tasks = tmp_tasks.select_related('project', 'milestone', 'resp')
            active_sprints = PM_User.get_milestones_statistic(tasks=tmp_tasks)

            tmp_tasks = PM_Task.objects.filter(milestone__in=closed_sprints_ids, active=True, resp=user)
            tmp_tasks = tmp_tasks.order_by('resp__last_name', 'project__name', 'milestone__name')
            tmp_tasks = tmp_tasks.select_related('project', 'milestone', 'resp')
            closed_sprints = PM_User.get_milestones_statistic(tasks=tmp_tasks)

            tmp_tasks = PM_Task.objects.filter(
                Q(milestone__in=draft_sprints_ids) | Q(milestone__isnull=True)
            )
            tmp_tasks = tmp_tasks.filter(resp=user)
            tmp_tasks = tmp_tasks.filter(active=True)
            tmp_tasks = tmp_tasks.aggregate(planned_hours=Sum('planTime'))
            planned_hours = tmp_tasks['planned_hours']

            return {
                'user': user,
                'profile': profile,
                'title': user.first_name + ' ' + user.last_name,
                'allTaskClosed': allTasksClosed,
                'milestonesOpen': PM_Milestone.objects.filter(closed=False, id__in=[x['milestone__id'] for x in user.todo.filter(closed=False, milestone__isnull=False)
                                            .exclude(author=user)
                                                .values('milestone__id').annotate(dcount=Count('milestone__id'))]).count(),
                'milestonesClosed': PM_Milestone.objects.filter(closed=True, id__in=[x['milestone__id'] for x in user.todo.filter(closed=True, milestone__isnull=False)
                                            .exclude(author=user)
                                                .values('milestone__id').annotate(dcount=Count('milestone__id'))]).count(),
                'achievements': PM_User_Achievement.objects.filter(user=user).select_related('achievement', 'project'),
                'specialties': s,
                'tagWeight': tagWeight,
                'overdueTasks': overdueTasks,
                'overdueMilestones': PM_Milestone.objects.filter(overdue=True, closed=True, id__in=[x['milestone__id'] for x in user.todo.filter(closed=True, milestone__isnull=False)
                                            .exclude(author=user)
                                                .values('milestone__id').annotate(dcount=Count('milestone__id'))]).count(),
                'allPlanClosed': allPlanClosed,
                'velocity': velocity,
                'bugsQty': bugsQty,
                'quality': quality,
                'userProjectsOpenQty': userProjectsOpenQty,
                'userProjectsClosedQty': userProjectsClosedQty,
                'timers': [
                    {
                        'id': timer.id,
                        'date': timer.dateEnd,
                        'time': unicode(timer),
                        'task': timer.task.name,
                        'comment': timer.comment,
                        'task_url': timer.task.url
                    } for timer in userTimes
                ],
                'keys': [
                    {
                        'id': key.id,
                        'created_at': key.created_at,
                        'name': key.name
                    } for key in userKeys
                ],
                'bets': arUserBets,
                'project_roles': userRoles,
                'user_projects': userProjects,
                'userIsEqualCurrentUser': request.user.id == user.id,
                'current_user_is_admin': request.user.is_superuser or request.user.get_profile().is_heliard_manager,
                'task': {
                    #'summ':taskSum,
                    #'summPerMonth':taskSumPerMonth,
                    'list': tasksResult,
                    # 'observers': tasksObserverResult
                },
                'taskSumm': taskSum,
                'taskLastMonth': taskSumPerMonth,
                'projectsForAddUser': currentUserManagedProjects.exclude(id__in=[k.project.id for k in userRoles]),
                'roles': PM_Role.objects.all(),
                'taskTemplate': taskTemplate,
                'timeGraph': timeGraph,
                'payments': paymentsAndCredits,
                'competence': taskTagCoefficient,
                'competencePlace': taskTagPosition + 100,
                'active_sprints': active_sprints,
                'closed_sprints': closed_sprints,
                'planned_hours': planned_hours,
            }
        except User.DoesNotExist:
            pass
