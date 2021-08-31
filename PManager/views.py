# -*- coding:utf-8 -*-
import datetime
import os
import json
import urllib
from operator import itemgetter

from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models import Sum
from django.shortcuts import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.template import loader, RequestContext
from django.utils.html import escape
from django.views.generic import TemplateView

from PManager import widgets
from PManager.classes.logger.logger import Logger
from PManager.models import Agent, PM_Milestone, PM_User, PM_MilestoneDevPaymentApproval, PM_ProjectRoles, PM_Files
from PManager.models import Credit
from PManager.password_validation import make_random_password
from PManager.models import Feedback, PM_Project, PM_Notice, PM_Timer, PM_User_Achievement, PM_Task_Message, \
    Fee, Agreement

from PManager.models import PM_Task
from PManager.services.mind.task_mind_core import TaskMind
from PManager.viewsExt import headers
from PManager.viewsExt.tools import TextFilters
from PManager.viewsExt.tools import EmailMessage
from PManager.viewsExt.tools import set_cookie
from common.views.base_views import PermissionMixin


class Brains:
    @staticmethod
    def trainTasksBrains(request):
        net = TaskMind()
        tasksForBrain = PM_Task.objects.filter(
            closed=False, realDateStart__isnull=False, active=True
        ).order_by('?')[:5]
        net.train(tasksForBrain)
        return HttpResponse('trained')


class MainPage:
    @staticmethod
    def feedback(request, lang='ru'):
        projectId = int(request.GET.get('project', 0))
        userId = int(request.GET.get('user', 0))

        client = None
        project = None

        if userId and projectId:
            client = User.objects.get(id=userId)
            project = PM_Project.objects.get(id=projectId)

            if request.method == 'POST':
                el = Feedback(
                    user=client,
                    project=project,
                    meeting_time=request.POST.get('meeting_time', None),
                    demo_value=request.POST.get('demo_value', None),
                    standup=request.POST.get('standup', None),
                    speed=request.POST.get('speed', None),
                    quality=request.POST.get('quality', None),
                    notes_communications=request.POST.get('notes_communications', None),
                    notes_quality=request.POST.get('notes_quality', None),
                    rating=request.POST.get('rating', None),
                    notes_was=request.POST.get('notes_was', None),
                    notes_do=request.POST.get('notes_do', None),
                )
                el.save()
                return HttpResponseRedirect(request.get_full_path() + '&success=1')

        c = RequestContext(request, {
            'client': client,
            'project': project
        })
        return HttpResponse(loader.get_template('main/feedback_' + lang + '.html').render(c))

    @staticmethod
    def support(request):
        c = RequestContext(request)
        return HttpResponse(loader.get_template('main/support.html').render(c))

    @staticmethod
    def likeAPro(request):
        from robokassa.forms import RobokassaForm
        userFee = Fee.objects.filter(user=request.user).order_by('-id')
        c = RequestContext(request)
        fee = userFee.aggregate(Sum('value'))['value__sum'] or 0
        feeLatId = userFee[0].id if userFee else None
        if feeLatId:
            form = RobokassaForm(initial={
                'OutSum': fee,  # order.total,
                'InvId': feeLatId,  # order.id,
                'Desc': 'Пополнение счета Экспертная компания',  # order.name,
                'Email': request.user.email,
                'user': request.user.id,
                'request': ''
            })
            c.update(
                {
                    'fee': fee,
                    'form': form
                }
            )

        return HttpResponse(loader.get_template('main/pro.html').render(c))

    @staticmethod
    def promoTmp(request):
        c = RequestContext(request)
        return HttpResponse(loader.get_template('main/promo_tmp.html').render(c))

    @staticmethod
    def changePassword(request):
        message = ''
        uname = request.POST.get('username', None)
        if uname:
            try:
                user = User.objects.get(username=uname)
                password = make_random_password()
                user.set_password(password)
                user.save()

                context = {
                    'user_name': ' '.join([user.first_name, user.last_name]),
                    'user_login': user.username,
                    'user_password': password
                }

                mess = EmailMessage(
                    'hello_new_user',
                    context,
                    'Экспертная компания: сообщество профессионалов. Ваши регистрационные данные.'
                )
                mess.send([user.username])
                from tracker.settings import ADMIN_EMAIL
                mess.send([ADMIN_EMAIL])
                message = 'success'

            except User.DoesNotExist:
                message = 'not_found'

        c = RequestContext(request, {"message": message})
        return HttpResponse(loader.get_template('main/change_password.html').render(c))

    @staticmethod
    def auth(request):


        if all((request.method == 'POST', 'username' in request.POST, 'password' in request.POST)):
            username = request.POST['username']
            password = request.POST['password']

            user = authenticate(username=username, password=password)

            if user is None or not user.is_active:
                error = 'not_found' if user is None else 'not_active'
                return HttpResponse(
                    loader.get_template('main/unauth.html')
                        .render(RequestContext(request, {"error": error}))
                )

            login(request, user)
            if request.GET.get('from', '') == 'mobile':
                return HttpResponse('{"unauthorized": false}', content_type='application/json')
            else:
                backurl = request.POST.get('backurl', '/')
                return HttpResponseRedirect(backurl)

        elif 'logout' in request.GET and request.GET['logout'] == 'Y':

            logout(request)
            return HttpResponseRedirect('/login/')

        if request.GET.get('from', '') == 'mobile':
            if request.user.is_authenticated():
                return HttpResponse('{"unauthorized": false}', content_type='application/json')

        if request.user.is_authenticated():
            backurl = request.POST.get('backurl', '/')
            return HttpResponseRedirect(backurl)

        c = RequestContext(request)
        return HttpResponse(loader.get_template('main/unauth.html').render(c))

    @staticmethod
    def indexRender(request, widgetList=None, activeMenuItem=None, widgetParams={}):

        host = request.get_host()

        # if host.find('local') == -1 and (host.find('tracker.ru') == -1 or host.find('tracker.ru') == 0):
        #     return redirect('http://rubedite.tracker.ru')

        cType = 'text/html'
        mimeType = None
        bXls = request.GET.get('xls_output', False)

        agents = Agent.objects.filter(Q(Q(datetime__lt=datetime.datetime.now()) | Q(datetime__isnull=True)))
        for agent in agents:
            agent.process()

        headerValues = headers.initGlobals(request)
        if headerValues['REDIRECT']:
            return redirect(headerValues['REDIRECT'])

        # stop timers
        leastHours = datetime.datetime.now() - datetime.timedelta(hours=9)
        for timer in PM_Timer.objects.filter(dateStart__lt=leastHours, dateEnd__isnull=True):
            timer.delete()

        headerWidgets = []
        widgetsInTabs = []
        c = RequestContext(request, {})
        userTimer = None
        userAchievement = None
        messages = None
        messages_qty = 0
        aMessages = []
        pageTitle = ''

        agreementForApprove = None
        if request.user.is_authenticated():
            messages = PM_Task_Message.objects.filter(
                userTo=request.user,
                read=False
            ).order_by('-dateCreate')

            taskNumber = int(request.GET.get('number', 0))
            taskId = int(request.GET.get('id', 0))
            projectId = int(request.GET.get('project', 0))

            if projectId:
                if taskId:
                    messages = messages.exclude(
                        task=taskId,
                        project=projectId
                    )
                elif taskNumber:
                    messages = messages.exclude(
                        task__number=taskNumber,
                        project=projectId
                    )

            messages = messages.exclude(code="WARNING")
            messages_qty = messages.count()

            for mes in messages:
                setattr(mes, 'text', TextFilters.getFormattedText(escape(mes.text)))
                setattr(mes, 'text', TextFilters.convertQuotes(mes.text))
                aMessages.append(mes)

            if not widgetList:
                widgetList = ['chat', 'tasklist']

            unapprovedAgreements = Agreement.objects.filter(payer=request.user, approvedByPayer=False)
            unapprovedAgreementsResp = Agreement.objects.filter(resp=request.user, approvedByResp=False)

            if unapprovedAgreements:
                agreementForApprove = unapprovedAgreements[0]
            elif unapprovedAgreementsResp:
                agreementForApprove = unapprovedAgreementsResp[0]

            userTimer = PM_Timer.objects.filter(user=request.user, dateEnd__isnull=True)
            if userTimer:
                userTimer = userTimer[0]
                timerDataForJson = userTimer.getTime()
                timerDataForJson['started'] = True if not userTimer.dateEnd else False
                setattr(userTimer, 'jsonData', timerDataForJson)

            arPageParams = {
                'pageCount': 10,
                'page': int(request.POST.get('page', 1))
            }

            for widgetName in widgetList:
                widget = getattr(widgets, widgetName)
                if widgetName == 'tasklist':
                    widget = widget.widget(request, headerValues, widgetParams, [], arPageParams)
                else:
                    widget = widget.widget(request, headerValues, widgetParams, [])

                if widget:
                    if 'redirect' in widget:
                        return HttpResponseRedirect(widget['redirect'])
                    if 'title' in widget:
                        pageTitle = widget['title']

                    c.update({widgetName: widget})
                    if bXls:
                        templateName = 'xls'
                    else:
                        templateName = 'widget'

                    widgetHtml = loader.get_template("%s/templates/%s.html" % (widgetName, templateName)).render(c)

                    if 'tab' in widget and widget['tab']:
                        widgetsInTabs.append({
                            'code': widgetName,
                            'name': widget['name'],
                            'html': widgetHtml
                        })
                    else:
                        headerWidgets.append(widgetHtml)

            if request.is_ajax():
                if request.GET.get('modal', None) is not None:
                    t = loader.get_template('main/xhr_response_modal.html')
                else:
                    t = loader.get_template('main/xhr_response.html')
            else:
                if request.GET.get('frame_mode', False):
                    t = loader.get_template('index_frame.html')
                elif bXls:
                    cType = 'application/xls'
                    mimeType = 'application/xls'
                    t = loader.get_template('index_xls.html')
                else:
                    t = loader.get_template('index.html')

            c.update({'widget_header': u" ".join(headerWidgets)})
            c.update({'widgets': widgetsInTabs})

            uAchievement = PM_User_Achievement.objects.filter(user=request.user, read=False)
            userAchievement = uAchievement[0] if uAchievement and uAchievement[0] else None

            if userAchievement:
                if userAchievement.achievement.delete_on_first_view:
                    userAchievement.delete()
                else:
                    userAchievement.read = True
                    userAchievement.save()
        else:
            import re
            # if is not main page
            if re.sub(r'([^/]+)', '', request.get_full_path()) == '/':
                t = loader.get_template('main/promo.html')
            else:
                return HttpResponseRedirect('/login/?backurl=' + urllib.quote(request.get_full_path()))

        if not headerValues['FIRST_STEP_FORM']:
            cur_notice = PM_Notice.getForUser(
                request.user,
                request.get_full_path()
            )
            if cur_notice:
                # cur_notice.setRead(request.user)
                c.update({
                    'current_notice': cur_notice
                })

        c.update({
            'pageTitle': pageTitle,
            'activeMenuItem': activeMenuItem,
            'userTimer': userTimer,
            'currentProject': headerValues['CURRENT_PROJECT'],
            'userAchievement': userAchievement,
            'messages': aMessages,
            'messages_qty': messages_qty,
            'agreementForApprove': agreementForApprove,
            'activeWidget': headerValues['COOKIES']['ACTIVE_WIDGET'] if 'ACTIVE_WIDGET' in headerValues[
                'COOKIES'] else None
        })

        response = HttpResponse(t.render(c), content_type=cType, mimetype=mimeType)
        if bXls:
            response['Content-Disposition'] = 'attachment; filename="file.xls"'

        for key in headerValues['SET_COOKIE']:
            set_cookie(response, key, headerValues['SET_COOKIE'][key])

        return response

    @staticmethod
    def widgetUpdate(request, widget_name):
        headerValues = headers.initGlobals(request)
        if headerValues['REDIRECT']:
            return redirect(headerValues['REDIRECT'])

        widget = getattr(widgets, widget_name)
        widget = widget.widget(request, headerValues, {}, [])
        c = RequestContext(request, {})
        if widget:
            if 'redirect' in widget:
                return HttpResponseRedirect(widget['redirect'])
        c.update({widget_name: widget})
        return HttpResponse(loader.get_template("%s/templates/widget.html" % widget_name).render(c))

    @staticmethod
    def returnWidgetJs(widgetName, script_name='widget'):
        if not widgetName: return False
        fn = os.path.join(os.path.dirname(__file__), "widgets/%s/js/%s.js" % (widgetName, script_name))

        try:
            js = open(fn, 'r').read()
            return js
        except Exception:
            return ''

    @staticmethod
    def jsWidgetProxy(request, widget_name=None, script_name=''):
        if widget_name:
            if script_name == 'script': script_name = 'widget'

            return HttpResponse(MainPage.returnWidgetJs(widget_name, script_name), mimetype='text/javascript')

    @staticmethod
    def creditReport(request):

        filterUser = request.GET.get('user', None)
        filterPayer = request.GET.get('payer', None)
        aFilter = {}
        if filterUser:
            aFilter['user'] = filterUser
        if filterPayer:
            aFilter['payer'] = filterPayer

        if request.user.is_superuser:
            headerValues = headers.initGlobals(request)
            p = headerValues['CURRENT_PROJECT']

            credits = Credit.objects.filter(task__project=p, value__gt=0)
            if aFilter:
                credits = Credit.objects.filter(**aFilter)

            credits = credits.order_by('-pk')
            aCredits = []
            sumCreditUserTo = 0
            sumCreditUserFrom = 0
            for credit in credits:
                if credit.user and credit.user.id:
                    sumCreditUserTo += credit.value
                else:
                    sumCreditUserFrom += credit.value

                aCredits.append(credit)
            payments = Credit.objects.filter(value__lt=0).order_by('-pk')
            c = RequestContext(request, {})
            c.update({
                'credits': aCredits,
                'payments': payments,
                'sumFrom': sumCreditUserFrom,
                'sumManager': sumCreditUserFrom * 0.15,
                'total': (sumCreditUserFrom * 0.85 - sumCreditUserTo),
                'sumTo': sumCreditUserTo
            })
            t = loader.get_template('report/credit_report.html')
            return HttpResponse(t.render(c))



    @staticmethod
    def creditChart(request):

        project = request.GET.get('project', None)
        if project:
            projects = [project]
        else:
            projects = request.user.get_profile().managedProjects

        days = 30
        dateEnd = datetime.datetime.now()
        dateStart = dateEnd - datetime.timedelta(days=days)
        aSums = []
        sOut = 0
        sIn = 0
        pIn = 0
        pOut = 0
        for m in range(0, days + 1):
            date = dateStart + datetime.timedelta(days=m)
            credit = Credit.objects.filter(
                date__range=(datetime.datetime.combine(date, datetime.time.min),
                             datetime.datetime.combine(date, datetime.time.max)),
                project__in=projects
            )

            creditOut = credit.filter(user__isnull=False)
            creditIn = credit.filter(payer__isnull=False)

            sOut += sum(c.value for c in creditOut)
            sIn += sum(c.value for c in creditIn)

            payments = Credit.objects.filter(date__range=(datetime.datetime.combine(date, datetime.time.min),
                                                          datetime.datetime.combine(date, datetime.time.max)),
                                             project__in=projects, value__lt=0)

            paymentsOut = payments.filter(user__isnull=False)
            paymentsIn = payments.filter(payer__isnull=False)
            pOut += sum(c.value for c in paymentsOut)
            pIn += sum(c.value for c in paymentsIn)

            aSums.append({
                'date': date,
                'in': sIn,
                'pin': pIn,
                'out': sOut,
                'pout': pOut,
            })
        c = RequestContext(request, {
            'sums': aSums
        })
        t = loader.get_template('report/credit_chart.html')
        return HttpResponse(t.render(c))


def add_timer(request):
    if not request.user.is_authenticated:
        return redirect('/')

    headerValues = headers.initGlobals(request)

    userTasks = PM_Task.objects.filter(
        active=True,
        closed=False
        # resp=request.user
    ).exclude(status__code='not_approved')
    if headerValues['CURRENT_PROJECT']:
        userTasks = userTasks.filter(project=headerValues['CURRENT_PROJECT'])

    seconds = request.POST.get('seconds', 0)
    comment = request.POST.get('comment', '')
    task_id = request.POST.get('task_id', 0)

    if seconds and comment and task_id:
        task = userTasks.get(pk=int(task_id))
        if task:
            if task.canPMUserView(request.user.get_profile()):
                # add timer
                dateEnd = datetime.datetime.now() + datetime.timedelta(seconds=int(seconds))
                timer = PM_Timer(dateEnd=dateEnd, seconds=seconds, task=task, user=request.user, comment=comment)
                timer.save()
                # add comment
                comment = PM_Task_Message(
                    task=task, text=str(timer) + '<br />' + comment, author=request.user, project=task.project,
                    hidden_from_clients=True)
                comment.save()
                # add user log
                logger = Logger()
                logger.log(request.user, 'DAILY_TIME', seconds, task.project.id)
                return redirect(
                    '/add_timer/?' + 'project=' + str(comment.project.id) + '&text=' + u'Успешно%20добавлено')
            else:
                return HttpResponse('Operation not permitted')

    tasks = []
    for task in userTasks:
        if not task.subTasks.filter(active=True).count():
            tasks.append(task)

    c = RequestContext(request, {
        'tasks': tasks
    })

    t = loader.get_template('report/add_timer.html')

    return HttpResponse(t.render(c))


class PaymentReport(PermissionMixin, TemplateView):
    template_name = 'report/payment_report.html'

    class PaymentRow(object):
        date_format = '%Y-%m-%d'
        ml_id = None
        user_id = None
        user = None
        is_developer = False
        user_role = None
        project = None
        ml_name = None
        ml_state = None
        ml_manager = None
        ml_start_date = None
        ml_plan_end_date = None
        ml_fact_end_date = None
        ml_delay = None
        ml_final_delay = None
        ml_hours = None

        hours_plan = 0
        hours_fact = 0
        sum_plan1 = 0
        sum_plan2 = 0
        sum_fact1 = 0
        sum_fact2 = 0
        total = 0

        is_approved = None

        def _date_format(self, date):
            if date:
                return datetime.datetime.strftime(date, self.date_format)
            else:
                return '-'

        def update_common_attribute(self, payment):
            self.ml_id = payment.milestone_id
            self.user_id = payment.user_id
            self.user = payment.user.get_full_name()
            self.is_developer = bool(payment.task)
            self.project = payment.milestone.project.name
            self.ml_name = payment.milestone.name
            self.ml_state = payment.milestone.get_state_name()
            self.ml_manager = payment.milestone.manager.get_full_name()
            self.ml_start_date = self._date_format(payment.milestone.start_date)
            self.ml_plan_end_date = self._date_format(payment.milestone.get_plan_end_date())
            self.ml_fact_end_date = self._date_format(payment.milestone.get_real_end_date())
            self.ml_delay = payment.milestone.delay_days
            self.ml_final_delay = payment.milestone.final_delay
            self.ml_hours = int(payment.milestone.type) + payment.milestone.extra_hours
            if self.is_developer:
                self.user_role = u'Разработка'
                self.update_sums = self._update_sum_developer
                try:
                    approve = PM_MilestoneDevPaymentApproval.objects.get(milestone=payment.milestone, user=payment.user)
                except PM_MilestoneDevPaymentApproval.DoesNotExist:
                    pass
                else:
                    self.is_approved = approve.is_approved
            else:
                self.user_role = u'Ведение проекта'
                self.update_sums = self._update_sum_manager

        def _update_sum_developer(self, payment):
            if payment.type == '0' and payment.code == '1':
                self.sum_plan1 += payment.value
                self.hours_plan += payment.task.planTime
            elif payment.type == '0' and payment.code == '2':
                self.sum_plan2 += payment.value
            elif payment.type == '1' and payment.code == '1':
                self.sum_fact1 += payment.value
                self.hours_fact += payment.task.planTime
            elif payment.type == '1' and payment.code == '2':
                self.sum_fact2 += payment.value
            self.total = self.sum_fact1 + self.sum_fact2

        def _update_sum_manager(self, payment):
            if payment.type == '0' and payment.code == '1':
                self.sum_plan1 += payment.value
            elif payment.type == '0' and payment.code == '3':
                self.sum_plan2 += payment.value
            elif payment.type == '1' and payment.code == '1':
                self.sum_fact1 += payment.value
            elif payment.type == '1' and payment.code == '3':
                self.sum_fact2 += payment.value
            self.total = self.sum_fact1 + self.sum_fact2

        def add_payment(self, payment):
            if not self.ml_id:
                self.update_common_attribute(payment)
            self.update_sums(payment)

        def is_need_save(self, payment):
            return not(self.ml_id == payment.milestone_id and self.user_id == payment.user_id and
                       self.is_developer == bool(payment.task))

        @property
        def is_not_zero(self):
            return self.sum_plan1 or self.sum_plan2 or self.sum_fact1 or self.sum_fact2

    def get_context_data(self, **kwargs):
        payments_list = list()

        context = super(PaymentReport, self).get_context_data(**kwargs)

        payments = Credit.objects.all()
        payments = payments.select_related('milestone', 'task', 'milestone__project', 'user')
        payments = payments.order_by('milestone', 'user', 'task', 'type')
        if payments:
            payments_iter = iter(payments)
            payment_row = self.PaymentRow()
            payment_row.add_payment(next(payments_iter))
            for payment in payments_iter:
                if payment_row.is_need_save(payment):
                    if payment_row.is_not_zero:
                        payments_list.append(vars(payment_row))
                    payment_row = self.PaymentRow()
                payment_row.add_payment(payment)
            payments_list.append(vars(payment_row))

        context['payments'] = payments_list
        return context


class MilestonesReport(PermissionMixin, TemplateView):
    template_name = 'report/milestones_report.html'

    class MilestoneRow(object):
        date_format = '%Y-%m-%d'
        id = None
        project = None
        name = None
        state = None
        manager = None
        start_date = None
        plan_end_date = None
        fact_end_date = None
        delay = 0
        final_delay = 0
        delay_deduction = 0

        base_hours = 0
        extra_hours = 0
        total_hours = 0
        tasks_hours = 0
        half_completed = '-'
        grooming = '-'
        credit = 0
        debit = 0

        def __init__(self, milestone):
            self.id = milestone.id
            self.project = milestone.project.name
            self.name = milestone.name
            self.state = milestone.get_state_name()
            self.manager = self.get_manager_name(milestone.manager)
            self.start_date = self._date_format(milestone.start_date)
            self.plan_end_date = self._date_format(milestone.get_plan_end_date())
            self.fact_end_date = self._date_format(milestone.get_fact_end_date())
            self.delay = milestone.delay_days
            self.final_delay = milestone.final_delay
            self.delay_deduction = milestone.delay_deduction
            self.base_hours = self.get_hours(milestone.type)
            self.extra_hours = self.get_hours(milestone.extra_hours)
            self.total_hours = self.base_hours + self.extra_hours
            self.tasks_hours = milestone.hrs
            self.half_completed = '+' if milestone.is_half_completed else '-'
            self.grooming = '+' if milestone.is_has_grooming else '-'
            self.credit, self.debit = self.get_payments_data(milestone)

        def _date_format(self, date):
            if date:
                return datetime.datetime.strftime(date, self.date_format)
            else:
                return '-'

        def get_manager_name(self, user):
            if user:
                return user.get_full_name()
            return '-'

        def get_hours(self, hours):
            if hours:
                try:
                    return float(hours)
                except ValueError:
                    pass
            return 0

        def get_payments_data(self, milestone):
            credit = 0
            debit = 0
            for payment in Credit.objects.filter(milestone=milestone):
                if payment.type == '0':
                    credit += payment.value
                else:
                    debit += payment.value
            return credit, debit

    def get_context_data(self, **kwargs):
        context = super(MilestonesReport, self).get_context_data(**kwargs)
        milestones = PM_Milestone.objects.all()
        ml_list = list()
        for ml in milestones:
            ml_list.append(vars(self.MilestoneRow(ml)))
        context['milestones'] = ml_list
        return context


class DeveloperWorkLoadReport(PermissionMixin, TemplateView):
    template_name = 'report/users_workload_report.html'

    def get_order(self, field_name, current_field, current_order):
        return 'asc' if field_name == current_field and current_order == 'desc' else 'desc'

    def get_context_data(self, **kwargs):
        context = super(DeveloperWorkLoadReport, self).get_context_data(**kwargs)

        current_sort_field = self.request.GET.get('sort_field')
        current_sort_order = self.request.GET.get('sort_order')

        active_ml_ids = PM_Milestone.get_active_milestones_ids()

        # tasks in active sprints
        tasks = PM_Task.objects.filter(milestone__in=active_ml_ids, active=True, resp__isnull=False)
        tasks = tasks.order_by('resp__last_name', 'project__name', 'milestone__name')
        tasks = tasks.select_related('project', 'milestone', 'resp')

        milestones_by_user = PM_User.get_milestones_statistic(tasks=tasks)

        if current_sort_order and current_sort_field:
            milestones_by_user = sorted(
                milestones_by_user,
                key=itemgetter(current_sort_field),
                reverse=current_sort_order == 'desc'
            )

        context['users'] = milestones_by_user
        context['sort_field'] = current_sort_field
        context['sort_order'] = current_sort_order
        context['sort_orders'] = {
            'name': self.get_order('name', current_sort_field, current_sort_order),
            'hours_all': self.get_order('hours_all', current_sort_field, current_sort_order),
            'workload': self.get_order('workload', current_sort_field, current_sort_order),
        }
        return context
    
    
def ApiPostTask(request):
    PROJECT = request.POST[u'project'].split('.docx')[0]
    TASK = json.loads(request.POST['task'].encode('utf-8'))
    LAST_NAME_USER = request.POST[u'user']
    USER = User.objects.get(last_name=LAST_NAME_USER).id

    """Поиск уже созданного проекта"""
    project = PM_Project.objects.filter(name=PROJECT)
    if project.count() == 0:
        """Создание проекта"""
        project = PM_Project(name=PROJECT, description='', author_id=USER, tracker_id=1, payer_id=USER,
                             settings='{"color_name_yellow": "\u0421\u043f\u043e\u0440\u043d\u044b\u0435 '
                                      '\u043f\u0443\u043d\u043a\u0442\u044b", "color_name_red": '
                                      '"\u041e\u0431\u043e\u0440\u0443\u0434\u043e\u0432\u0430\u043d\u0438\u0435", '
                                      '"use_colors_in_kanban": "1", "color_name_purple": "", "color_name_blue": '
                                      '"\u0412\u0441\u044f \u0430\u0440\u0435\u043d\u0434\u0430", "color_name_grey": '
                                      '"", "color_name_orange": "", "save": '
                                      '"\u041f\u0440\u0438\u043c\u0435\u043d\u0438\u0442\u044c", "client_comission": '
                                      '"", "color_name_green": ""}',
                             )
        project.save()
        project_role = PM_ProjectRoles(user_id=USER, project_id=project.id, role_id=2)
        project_role.save()
        project_role = PM_ProjectRoles(user_id=2, project_id=project.id, role_id=3)
        project_role.save()
    else:
        project = PM_Project.objects.get(name=PROJECT)
        
    for el in TASK:
        if el.__len__() == 1:
            task_name = TASK[el]
            task1 = PM_Task.objects.create(name=task_name, resp_id=USER, number=1, project_id=project.id,
                                           author_id=USER)

    for el in TASK:
        if el.__len__() == 2:
            task_name = TASK[el]
            parentTask = PM_Task.objects.get(name=TASK[el[:1]], resp_id=USER, project_id=project.id, author_id=USER)
            task2 = PM_Task.objects.create(name=task_name, resp_id=USER, parentTask=parentTask, number=1,
                                           project_id=project.id, author_id=USER)

    for el in TASK:
        if el.__len__() == 3:
            task_name = TASK[el]
            parentTask = PM_Task.objects.get(name=TASK[el[:2]], resp_id=USER, project_id=project.id, author_id=USER)
            task3 = PM_Task.objects.create(name=task_name, resp_id=USER, parentTask=parentTask, number=1,
                                           project_id=project.id, author_id=USER)

    for el in TASK:
        if el.__len__() == 4:
            task_name = TASK[el]
            parentTask = PM_Task.objects.get(name=TASK[el[:3]], resp_id=USER, project_id=project.id, author_id=USER)
            task4 = PM_Task.objects.create(name=task_name, resp_id=USER, parentTask=parentTask, number=1,
                                           project_id=project.id, author_id=USER)

    for el in TASK:
        if el.__len__() == 5:
            task_name = TASK[el]
            parentTask = PM_Task.objects.get(name=TASK[el[:4]], resp_id=USER, project_id=project.id, author_id=USER)
            task5 = PM_Task.objects.create(name=task_name, resp_id=USER, parentTask=parentTask, number=1,
                                           project_id=project.id, author_id=USER)
    return HttpResponse()

def ApiPostText(request):
    PROJECT = request.POST[u'project'].split('.docx')[0]
    TASK = json.loads(request.POST['task'].encode('utf-8'))
    LAST_NAME_USER = request.POST[u'user']
    USER = User.objects.get(last_name=LAST_NAME_USER).id
    TEXT = request.POST[u'text']

    project = PM_Project.objects.get(name=PROJECT)
    task = PM_Task.objects.get(name=TASK, resp_id=USER, project_id=project.id, author_id=USER)
    task.text = TEXT
    task.save()
    return HttpResponse()

def ApiPostFile(request):
    from django.core.files.storage import FileSystemStorage
    PROJECT = request.POST[u'project'].split('.docx')[0]
    TASK = request.POST[u'task']
    TEXT = request.POST[u'text']
    LAST_NAME_USER = request.POST[u'user']
    USER = User.objects.get(last_name=LAST_NAME_USER).id

    FILE = request.FILES.get('uploaded_file')
    fs = FileSystemStorage()
    filename = fs.save(FILE.name, FILE)

    project = PM_Project.objects.get(name=PROJECT)
    task = PM_Task.objects.get(name=TASK, project_id=project.id)

    file = PM_Files(file=filename, authorId_id=USER, projectId_id=project.id,
                    name=filename)

    file.save()
    task.files.add(file)
    return HttpResponse()
