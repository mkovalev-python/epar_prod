# -*- coding:utf-8 -*-
__author__ = 'Gvammer'

import copy
import datetime
import hashlib
import json
from datetime import timedelta

import pytz
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.core.validators import MaxLengthValidator
from django.db import models
from django.db.models import Q
from django.db.models import Sum
from django.db.models.signals import post_save, pre_delete, post_delete, pre_save
from django.template import Template, Context
from django.utils import timezone
from django.utils.formats import localize
from django.utils.timezone import now

from PManager.classes.datetime.work_time import WorkTime
from PManager.classes.language import transliterate
from PManager.classes.logger.logger import Logger
from PManager.classes.server.message import RedisMessage
from PManager.customs.storages import path_and_rename
from PManager.models.morphy import trackMorphy
from PManager.services.service_queue import service_queue
from PManager.viewsExt.tools import EmailMessage
from PManager.viewsExt.tools import templateTools
from tracker.settings import COMISSION

import logging
logger = logging.getLogger(__name__)


def redisSendTaskUpdate(fields):
    mess = RedisMessage(service_queue,
                        objectName='task',
                        type='update',
                        fields=fields)
    mess.send()


def redisSendLogMessage(fields):
    mess = RedisMessage(service_queue,
                        objectName='comment',
                        type='add',
                        fields=fields)
    mess.send()


class Tags(models.Model):
    tagText = models.CharField(max_length=100, db_index=True)
    frequency = models.FloatField(default=0)
    weight = 0

    def __unicode__(self):
        return self.tagText

    class Meta:
        app_label = 'PManager'


class ObjectTags(models.Model):
    tag = models.ForeignKey(Tags, related_name='objectLinks')
    weight = models.PositiveIntegerField(default=0)
    content_type = models.ForeignKey(ContentType, db_index=True)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        app_label = 'PManager'

    @classmethod
    def get_weights(cls, tag_ids, content_type_id, obj_id=None, filter_content=[], order_by=(), limit=None):
        request_str = 'SELECT SUM(`weight`) as weight_sum, `id`, `object_id`, `content_type_id` ' + \
                      'from PManager_objecttags WHERE tag_id in (' + \
                      ', '.join(tag_ids) + ') AND content_type_id=' + \
                      str(content_type_id)
        if obj_id is not None:
            request_str += ' AND object_id=' + str(obj_id)
        if filter_content:
            request_str += ' AND object_id IN (' + ', '.join(str(x) for x in filter_content) + ')'
        request_str += " GROUP BY object_id"
        if order_by and len(order_by) == 2:
            request_str += " ORDER BY %s %s" % order_by
        if limit is not None:
            request_str += " LIMIT %s" % limit
        return cls.objects.raw(request_str)


class PM_Tracker(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    dateCreate = models.DateTimeField(auto_now_add=True, blank=True)
    description = models.TextField(null=True)
    admin = models.ForeignKey(User, related_name='createdTrackers', null=True)
    logo = models.ImageField(upload_to="tracker/media/trackers/", null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'PManager'


class PM_Project(models.Model):
    id_md5 = models.CharField(max_length=32, null=True, editable=False)
    name = models.CharField(max_length=255, verbose_name=u'Название')
    dateCreate = models.DateTimeField(auto_now_add=True, blank=True)
    description = models.TextField(null=True, verbose_name=u'Описание')
    author = models.ForeignKey(User, related_name='createdProjects')
    image = models.ImageField(upload_to=path_and_rename("project_thumbnails"), null=True, verbose_name=u'Изображение')
    tracker = models.ForeignKey(PM_Tracker, related_name='projects')
    repository = models.CharField(max_length=255, blank=True, verbose_name=u'Репозиторий')
    api_key = models.CharField(max_length=200, blank=True, verbose_name=u'Ключ проекта')
    closed = models.BooleanField(blank=True, verbose_name=u'Архив', default=False, db_index=True)
    locked = models.BooleanField(blank=True, verbose_name=u'Заблокирован', default=False, db_index=True)
    settings = models.CharField(max_length=1000)
    payer = models.ForeignKey(User)

    class Meta:
        app_label = 'PManager'
        ordering = ('name',)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        manager_role = None
        users = None
        if not self.id:
            self.payer = self.author
            try:
                manager_role = PM_Role.objects.get(code='manager')
            except PM_Role.DoesNotExist:
                pass

            users = User.objects.filter(is_active=True, groups__name='rubedite_team')
        else:
            self.id_md5 = hashlib.md5(u'{}:salt'.format(self.id)).hexdigest()
        super(self.__class__, self).save(*args, **kwargs)
        if manager_role and users:
            project_roles = []
            for user in users:
                project_roles.append(PM_ProjectRoles(user=user, project=self, role=manager_role))

            PM_ProjectRoles.objects.bulk_create(project_roles)

    @property
    def url(self):
        return '/?project=' + str(self.id)

    @property
    def support_url(self):
        if self.id_md5:
            return reverse('support_page:project-form', kwargs={'hash': self.id_md5})
        else:
            return ''

    @property
    def imagePath(self):
        return unicode(self.image).replace('PManager', '')

    def setSettings(self, settings):
        self.settings = json.dumps(settings)

    def getSettings(self):
        return json.loads(self.settings) if self.settings else {}

    def generate_rep_name(self):
        if (self.repository):
            return self.repository
        return transliterate(self.name)

    def openMilestones(self):
        return PM_Milestone.objects.filter(
            project=self.id,
            closed=0,
        )

    def getUsers(self):
        users = PM_ProjectRoles.objects.filter(project=self).values_list('user', flat=True)
        return User.objects.filter(pk__in=users).distinct()


class Release(models.Model):
    statuses = (
        ('ready', u'Собран'),
        ('done', u'Выпущен'),
        ('new', u'Новый')
    )

    name = models.CharField(max_length=255)
    date = models.DateTimeField()
    status = models.CharField(max_length=30, choices=statuses, default='new')
    description = models.CharField(max_length=1000, blank=True, null=True)
    project = models.ForeignKey(PM_Project, related_name='releases')
    active = models.BooleanField(default=True, blank=True)

    class Meta:
        app_label = 'PManager'


class PM_File_Category(models.Model):
    name = models.CharField(max_length=200)
    #    category = models.ManyToManyField('self', null=True, blank=True, related_name='childrens')
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')
    projects = models.ManyToManyField('PM_Project', null=True, blank=True, related_name='file_categories')

    class Meta:
        app_label = 'PManager'


class PM_Files(models.Model):
    file = models.FileField(max_length=400, upload_to=path_and_rename("projects", 'str(instance.projectId.id)'))
    authorId = models.ForeignKey(User, null=True)
    projectId = models.ForeignKey(PM_Project, null=True)
    category = models.ForeignKey(PM_File_Category, related_name="files", null=True, blank=True)
    versions = models.ManyToManyField('self', related_name="newVersions", null=True, blank=True)
    is_old_version = models.NullBooleanField(null=True, blank=True)
    date_create = models.DateTimeField(auto_now_add=True, blank=True)
    name = models.CharField(max_length=200, null=True)
    double = models.BooleanField(default=False, blank=True)
    attach = models.BooleanField(default=False, blank=True)

    def __unicode__(self):
        s = unicode(self.file)
        if not s.startswith(u'media/'): s = u'media/' + s
        if not s.startswith(u'/'): s = u'/' + s
        return s

    def __str__(self):
        s = str(self.file)
        if not s.startswith('media/'): s = 'media/' + s
        if not s.startswith('/'): s = '/' + s
        return s

    def save(self, *args, **kwargs):
        if not self.name:
            import ntpath

            self.name = ntpath.basename(self.src)

        super(self.__class__, self).save(*args, **kwargs)

    @property
    def isPicture(self):
        return str(self).endswith('.jpg') or str(self).endswith('.gif') or str(self).endswith('.png')

    @property
    def src(self):
        url = self.__str__()
        if url.startswith('/'):
            url = url[1:]
        return '/protected/' + url

    @property
    def type(self):
        return str(self.file).split('.')[-1]

    @property
    def size(self):
        import os

        try:
            if os.path.isfile(self.file.path):
                size = os.path.getsize(os.path.join(os.path.dirname(__file__), '..' + self.src).replace('\\', '/'))
                if 10 ** 3 < size < 10 ** 6:
                    size = str(size / (10 ** 3)) + 'K'
                elif 10 ** 6 < size < 10 ** 9:
                    size = str(size / (10 ** 6)) + 'Mb'
                elif 10 ** 9 < size:
                    size = str(size / (10 ** 9)) + 'Gb'
                return size
        except Exception:
            pass
        return ''

    @property
    def hasOldVersions(self):
        return self.versions.all().count() > 0

    def addNewVersion(self, oFile):
        oFile.versions = copy.copy(self.versions.all())
        oFile.versions.add(self)

        if oFile.save():
            self.is_old_version = True
            self.save()
            return True

        return False

    def getJson(self):
        return {
            'type': self.type,
            'src': self.src,
            'isPicture': self.isPicture,
            'id': self.id,
            'name': self.name,
            'size': self.size,
            'date_create': self.date_create.strftime('%d.%m.%Y %H:%M:%S'),
            'hasOldVersions': self.hasOldVersions
        }

    class Meta:
        app_label = 'PManager'


class PM_Task_Status(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'PManager'


class PM_Milestone(models.Model):
    THRESHOLD_DANGER = 1.1
    THRESHOLD_WARNING = 1.3
    STATUS_DANGER = 'danger'
    STATUS_WARNING = 'warning'
    STATUS_NORMAL = 'success'
    crit_choices = (
        (1, u'Не критичная'),
        (2, u'Средняя'),
        (3, u'Критичная'),
    )

    TYPE_56 = '56'
    TYPE_38 = '38'
    TYPE_S_10 = '10'
    TYPE_S_20 = '20'
    TYPE_OTHER = 'other'
    type_choices = (
        (TYPE_56, u'56 часов'),
        (TYPE_S_10, u'техподдержка 10 часов'),
        (TYPE_S_20, u'техподдержка 20 часов'),
        (TYPE_OTHER, u'Другой'),
    )
    id_md5 = models.CharField(max_length=32, null=True, editable=False)
    name = models.CharField(max_length=255)
    text = models.CharField(max_length=4000, blank=True, null=True, default='')
    target = models.CharField(u'Цель', max_length=4000, blank=True, null=True, default='')
    criteria = models.CharField(u'Критерий приемки', max_length=4000, blank=True, null=True, default='')
    file_for_client = models.FileField(u'Файл для клиента', upload_to='for_client/', blank=True, null=True)
    date = models.DateTimeField(u'Плановая дата окончания', null=True, blank=True)
    date_create = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    critically = models.IntegerField(blank=True, null=True, default=2, choices=crit_choices)
    extra_hours = models.IntegerField(null=True, default=0)
    project = models.ForeignKey(PM_Project, related_name='milestones')
    overdue = models.BooleanField(blank=True)
    delay_deduction = models.IntegerField(u'Вычет просрочки', default=0)
    final_delay = models.IntegerField(u'Итоговая просрочка', blank=True, null=True)

    responsible = models.ManyToManyField(User, null=True, blank=True)
    closed = models.BooleanField(blank=True, default=False)
    manager = models.ForeignKey(User, related_name='milestones', null=True, blank=True, verbose_name=u'ответственный менеджер')
    # todo need to make field 'type' not nullable
    type = models.CharField(u'Тип спринта', max_length=25, default=0, db_index=True, blank=True, null=True)
    # todo need to remove this field and make code refactoring
    fact_close_date = models.DateTimeField(u'Фактическая дата закрытия', null=True, blank=True)

    is_close_confirmed = models.BooleanField(u'Закрытие подтверждено клиентом', default=False)

    is_half_completed = models.FloatField(u'51% задач закрыто', default=0)
    is_has_grooming = models.FloatField(u'Груминг', default=0)
    delay_factor = models.FloatField(u'Коэффициент просрочки', default=0)
    g_factor = models.FloatField(u'Коэффициент G', default=0)

    class Meta:
        app_label = 'PManager'

    def __unicode__(self):
        return self.project.name + ': ' + self.name

    def save(self, *args, **kwargs):
        if self.id:
            self.id_md5 = hashlib.md5(u'{}:salt'.format(self.id)).hexdigest()
        super(PM_Milestone, self).save(*args, **kwargs)

    @property
    def support_url(self):
        if self.id_md5:
            return reverse('support_page:milestone-form', kwargs={'hash': self.id_md5})
        else:
            return ''

    @classmethod
    def create_milestone(cls, name, project, manager):

        sprint = cls.objects.create(
            name=name,
            project=project,
            manager=manager,
            date=None
        )
        sprint.set_status(PM_MilestoneStatus.STATUS_DRAFT, manager)
        return sprint

    def start_milestone(self, target, type, date, user):
        self.target = target
        self.type = type
        self.date = date
        self.save()
        self.set_status(
            status=PM_MilestoneStatus.STATUS_STARTED,
            start_date=datetime.date.today(),
            end_date=date,
            user=user
        )

    def rate_milestone(self, extra_hours, criteria, user):
        self.extra_hours = extra_hours
        self.criteria = criteria
        self.save()
        self.set_status(PM_MilestoneStatus.STATUS_RATED, user)

        from PManager.models import Credit
        Credit().add_credit_manager(self.manager, self)
        for task in self.tasks.filter(active=True):
            if task.resp:
                Credit().add_credit_developer(task.resp, self, task)

    def pause_milestone(self, reason, user):
        map_status = {
            PM_MilestoneStatus.STATUS_STARTED: PM_MilestoneStatus.STATUS_PAUSED_AFTER_STARTED,
            PM_MilestoneStatus.STATUS_RATED: PM_MilestoneStatus.STATUS_PAUSED_AFTER_RATED,
        }
        status = map_status[self.state]
        self.set_status(status=status, comment=reason, user=user)

    def resume_milestone(self, end_date, user):
        map_status = {
            PM_MilestoneStatus.STATUS_PAUSED_AFTER_STARTED: PM_MilestoneStatus.STATUS_STARTED,
            PM_MilestoneStatus.STATUS_PAUSED_AFTER_RATED: PM_MilestoneStatus.STATUS_RATED
        }
        status = map_status[self.state]
        self.set_status(status=status,
                        start_date=datetime.date.today(),
                        end_date=end_date,
                        user=user)

    def _is_half_completed(self):
        tasks = self.tasks.filter(active=True)
        if self.closed:
            k = 0
            m_hours = 0

            m_start_date = self.start_date

            if m_start_date:
                m_end_date = self.date.date()
                m_middle_day = m_start_date + (m_end_date - m_start_date) // 2

                for task in tasks:
                    m_hours += task.planTime
                    if task.dateClose.date() <= m_middle_day:
                        k += task.planTime

                return k and (k * 100 / m_hours >= 50)

            else:
                return False
        else:
            return False

    def _is_has_grooming(self):
        m_start_date = self.start_date
        m_end_date = self.date.date()
        tasks = PM_Task.objects.all()
        tasks = tasks.filter(active=True, closed=False, dateCreate__gte=m_start_date, dateCreate__lte=m_end_date)
        tasks = tasks.exclude(milestone_id=self.id)
        return len(tasks) > 1

    def _get_delay_factor(self):
        l = 0
        delays = self.final_delay
        if delays == 0:
            l = 1
        elif 0 < delays < 3:
            l = 0.7
        elif 3 <= delays < 6:
            l = 0.5
        return l

    def _get_g_factor(self):
        return 1

    def close_milestone(self, date, user):
        if self.get_state() and self.get_state().status != PM_MilestoneStatus.STATUS_RATED:
            return {'is_closed': False, 'message': 'Расчет может быть проведен только из статуса Оценен'}
        elif self.tasks.filter(active=True, closed=False):
            return {'is_closed': False, 'message': 'Утвердите пожалуйста все расчеты в смете'}
        else:
            self.final_delay = self.delay_days_w_deduction if self.final_delay is None else 0

            self.closed = True
            self.fact_close_date = date

            self.is_half_completed = self._is_half_completed()
            self.is_has_grooming = self._is_has_grooming()
            self.g_factor = self._get_g_factor()
            self.delay_factor = self._get_delay_factor()

            self.save()

            self.set_status(PM_MilestoneStatus.STATUS_CLOSED, user, end_date=now())

            from PManager.models import Credit
            # add credits to manager
            Credit().add_credit_manager(self.manager, self)

            #add credits to developers
            developers = set()
            for task in self.tasks.filter(active=True):
                if task.resp:
                    developers.add(task.resp_id)
                    Credit().add_credit_developer(task.resp, self, task)


            # add milestone payments approval status
            for developer in developers:
                try:
                    PM_MilestoneDevPaymentApproval(milestone=self, user_id=developer).save()
                except Exception as e:
                    logger.error(e)
            return {'is_closed': True, 'message': 'Группа расчетов закрыт'}

    def milestone_close_confirmed(self, user):
        self.is_close_confirmed = True
        self.save()
        self.set_status(status=PM_MilestoneStatus.STATUS_CLOSE_CONFIRMED, user=user)

    def set_status(self, status, user, start_date=None, end_date=None, comment=''):
        if start_date and end_date:
            self.date = end_date
            self.save(update_fields=['date'])

        if not comment:
            comment = u'{} установил статус: {} ({})'.format(user, status, now())
        self.statuses.create(
            author=user,
            status=status,
            comment=comment,
            start_date=start_date,
            end_date=end_date
        )

    def get_state(self):
        if self.statuses.exists():
            return self.statuses.latest('date_create')

    def get_state_name(self):
        if self.statuses.exists():
            return self.get_state().get_status_display()

    def get_name(self):
        name_list = [self.name, ]
        end_date = self.get_plan_end_date()
        if end_date:
            name_list.append("({:%d.%m.%Y})".format(end_date))
        elif self.date:
            name_list.append("({:%d.%m.%Y})".format(self.date))
        if self.get_state_name():
            name_list.append(u"- {}".format(self.get_state_name()))
        return u' '.join(name_list)

    @property
    def state(self):
        if self.statuses.exists():
            return self.statuses.latest('date_create').status

    def tasksOrderedByClose(self):
        return self.tasks.filter(active=True).order_by('-closed', 'status__code')

    @property
    def start_date(self):
        statuses = self.statuses.exclude(start_date__isnull=True)
        if statuses.exists():
            return statuses.latest('date_create').start_date

    @property
    def end_date(self):
        statuses = self.statuses.filter(start_date__isnull=True).exclude(end_date__isnull=True)
        if statuses.exists():
            return statuses.latest('date_create').end_date
        else:
            return None

    @property
    def hrs(self):
        return self.tasks.filter(active=True).aggregate(Sum('planTime'))['planTime__sum'] or 0

    @property
    def userHours(self):

        userHours = {}
        summ = 0
        for task in self.tasks.filter(active=True):
            if task.resp:
                bet = task.resp.get_profile().getBet(task.project)
                if bet is not None:
                    if task.resp.email not in userHours:
                        userHours[task.resp.email] = {
                            'name': task.resp.last_name + ' ' + task.resp.first_name if task.resp.last_name else task.resp.email,
                            'hrs': 0,
                            'price': 0
                        }

                    userHours[task.resp.email]['hrs'] += task.planTime
                    userHours[task.resp.email]['price'] += task.planTime * bet
                    summ += task.planTime * bet

        return {
            'elements': userHours,
            'sum': summ
        }

    @staticmethod
    def check():
        milestones = PM_Milestone.objects.filter(
            overdue=False,
            closed=False,
            date__lte=datetime.datetime.now()
        )
        for ms in milestones:
            if ms.delay_days_w_deduction and ms.tasks.exists() and ms.tasks.filter(closed=False).exists():
                ms.overdue = True
                ms.save()


                for user in ms.responsible.all():
                    message = PM_Task_Message(
                        userTo=user,
                        text=u'Группа расчетов "' + ms.name + u'" просрочен',
                        code='MILESTONE_OVERDUE',
                        project=ms.project
                    )
                    message.save()

    def status(self):
        plan_time_max = self.tasks.filter(active=True, closed=0)
        plan_time_max = plan_time_max.values('resp_id')
        plan_time_max = plan_time_max.annotate(sumtime=Sum('planTime'))
        plan_time_max = plan_time_max.order_by('-sumtime')
        if plan_time_max:
            task_hours = plan_time_max[0]['sumtime']
            if task_hours:
                end_date = self.date
                if timezone.is_naive(self.date):
                    end_date = timezone.make_aware(self.date, timezone.get_default_timezone())
                time_needed = WorkTime(startDateTime=datetime.datetime.now(),
                                       taskHours=task_hours * self.THRESHOLD_DANGER)
                if time_needed.endDateTime >= end_date:
                    return self.STATUS_DANGER

                time_needed = WorkTime(startDateTime=datetime.datetime.now(),
                                       taskHours=task_hours * self.THRESHOLD_WARNING)
                if time_needed.endDateTime >= end_date:
                    return self.STATUS_WARNING

        return self.STATUS_NORMAL

    def percent(self):
        plan_time_table = self.tasks.filter(active=True)
        plan_time_table = plan_time_table.values('closed')
        plan_time_table = plan_time_table.annotate(sumtime=Sum('planTime'))
        plan_time_table = plan_time_table.order_by('-closed')
        if plan_time_table:
            if len(plan_time_table) == 1:
                return 100 if plan_time_table[0]['closed'] else 0

            if len(plan_time_table) > 1 and plan_time_table[1].get('sumtime', 0) > 0:
                sumtime_0 = plan_time_table[0]['sumtime']
                sumtime_1 = plan_time_table[1]['sumtime']
                percent = sumtime_0 * 100 / (sumtime_0 + sumtime_1)
                return int(round(percent, 0))
        return 0

    def daysLeft(self):
        timeSpan = self.date - timezone.make_aware(datetime.datetime.now(), timezone.get_current_timezone())
        return timeSpan.days

    def _get_date_from_datetime(self, date):
        if date:
            tz = pytz.timezone(settings.TIME_ZONE)
            if date.tzinfo is None:
                return tz.localize(date).date()
            else:
                return date.astimezone(tz).date()
        return None

    def get_plan_end_date(self):
        return self._get_date_from_datetime(self.date)

    def get_real_end_date(self):
        if self.fact_close_date:
            return self._get_date_from_datetime(self.fact_close_date)
        elif self.get_plan_end_date() and now().date() > self.get_plan_end_date():
            return now().date()
        else:
            return None

    def get_fact_end_date(self):
        if self.fact_close_date:
            return self._get_date_from_datetime(self.fact_close_date)
        else:
            return None

    @property
    def delay_days(self):
        delay = cache.get('milestone_{id}_delay'.format(id=self.id))
        if delay is None:
            delay = 0
            plan_end_date = self.get_plan_end_date()
            real_end_date = self.get_real_end_date()
            if plan_end_date and real_end_date:
                holidays = PM_Holidays.objects.filter(date__lte=now() + timedelta(days=1), date__gte=now() - timedelta(days=60))
                holidays = holidays.values_list('date', flat=True)
                d = (real_end_date - plan_end_date).days
                daygenerator = (plan_end_date + timedelta(x + 1) for x in xrange((real_end_date - plan_end_date).days))
                for day in daygenerator:
                    if day.weekday() < 5 and day not in holidays:
                        delay += 1
        return delay

    @property
    def delay_days_w_deduction(self):
        if self.final_delay is None:
            delay = self.delay_days - self.delay_deduction
            return delay if delay > 0 else 0
        else:
            return self.final_delay

    @classmethod
    def get_active_milestones_ids(cls):
        ml_started = PM_MilestoneStatus.objects.filter(status=PM_MilestoneStatus.STATUS_STARTED)
        ml_started = ml_started.values_list('sprint_id', flat=True)
        ml_closed = PM_MilestoneStatus.objects.filter(status=PM_MilestoneStatus.STATUS_CLOSED)
        ml_closed = ml_closed.values_list('sprint_id', flat=True)
        return set(ml_started) - set(ml_closed)

    @classmethod
    def get_draft_milestones_ids(cls):
        ml_draft = PM_MilestoneStatus.objects.filter(status=PM_MilestoneStatus.STATUS_DRAFT)
        ml_draft = ml_draft.values_list('sprint_id', flat=True)
        ml_started = PM_MilestoneStatus.objects.filter(status=PM_MilestoneStatus.STATUS_STARTED)
        ml_started = ml_started.values_list('sprint_id', flat=True)
        return set(ml_draft) - set(ml_started)

    @classmethod
    def get_closed_milestones_ids(cls):
        closed_ml_ids = cls.objects.filter(closed=True)
        closed_ml_ids = closed_ml_ids.values_list('id', flat=True)
        return set(closed_ml_ids)


class PM_MilestoneStatus(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_STARTED = 'started'
    STATUS_PAUSED_AFTER_STARTED = 'paused_started'
    STATUS_RATED = 'rated'
    STATUS_PAUSED_AFTER_RATED = 'paused_rated'
    STATUS_PAUSED = 'paused'
    STATUS_RESUMED = 'resumed'
    STATUS_CLOSED = 'closed'
    STATUS_CLOSE_CONFIRMED = 'close_confirmed'

    status_choices = (
        (STATUS_DRAFT, u'новый'),
        (STATUS_STARTED, u'начат'),
        (STATUS_PAUSED_AFTER_STARTED, u'приостановлен'),
        (STATUS_PAUSED_AFTER_RATED, u'приостановлен'),
        (STATUS_RATED, u'оценен'),
        (STATUS_PAUSED, u'приостановлен'),
        (STATUS_RESUMED, u'возобновлен'),
        (STATUS_CLOSED, u'закрыт'),
        (STATUS_CLOSE_CONFIRMED, u'закрытие подтверждено'),
    )

    messages = {
        STATUS_STARTED: (u'Группа расчетов начат. Проект {{sprint.project}}. {{sprint.name}}. {{manager}}. '
                         u'Плановая дата окончания: {{plan_close_date}}. '
                         u'{{sprint.type}} часов. Цель спринта: {{target}}.'),
        STATUS_RATED: (u'Группа расчетов оценен. Проект {{sprint.project}}. {{sprint.name}}. {{manager}}. '
                       u'{% if extra_hours %}Дополнительные часы: {{extra_hours}} часов. {% endif %}'
                       u'Критерии приемки: {{criteria}}.'),
        STATUS_PAUSED: (u'Группа расчетов приостановлен. Проект {{sprint.project}}. {{sprint.name}}. {{manager}}. '
                        u'Причина приостановки: {{reason}}.'),
        STATUS_PAUSED_AFTER_STARTED: (u'Группа расчетов приостановлен. Проект {{sprint.project}}. {{sprint.name}}. {{manager}}. '
                                      u'Причина приостановки: {{reason}}.'),
        STATUS_PAUSED_AFTER_RATED: (u'Группа расчетов приостановлен. Проект {{sprint.project}}. {{sprint.name}}. {{manager}}. '
                                    u'Причина приостановки: {{reason}}.'),
        STATUS_RESUMED: (u'Группа расчетов возобновлен. Проект {{sprint.project}}. {{sprint.name}}. {{manager}}. '
                         u'Новая плановая дата окончания: {{new_close_date}}.'),
        STATUS_CLOSED: (u'Группа расчетов закрыт. Проект {{sprint.project}}. {{sprint.name}}. {{manager}}. '
                        u'{% if delay_days %}Просрочка: {{delay_days}}дн. {% else %}Без просрочки!{% endif %}.'),
    }

    sprint = models.ForeignKey(PM_Milestone, related_name='statuses')
    author = models.ForeignKey(User, related_name='createdSpints', null=True, blank=True)
    status = models.CharField(u'Статус', max_length=15, db_index=True, choices=status_choices)
    start_date = models.DateField(u'Дата начала', null=True, blank=True)
    end_date = models.DateField(u'Дата конца', null=True, blank=True)
    comment = models.TextField(u'Комментарий', blank=True)
    date_create = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __unicode__(self):
        return u'Группа расчетов {sprint.name} - {status}'.format(sprint=self.sprint, status=self.status)

    class Meta:
        app_label = 'PManager'

    def save(self, *args, **kwargs):
        super(PM_MilestoneStatus, self).save(*args, **kwargs)
        self.send_notification()

    def send_notification(self):
        message = self.messages.get(self.status)
        if message:
            event_date = localize(now().date(), use_l10n=False)
            plan_close_date = self.sprint.get_plan_end_date()
            plan_close_date = localize(plan_close_date,  use_l10n=False) if plan_close_date else '-'
            new_close_date = localize(self.end_date,  use_l10n=False) if self.end_date else '-'

            data = Context({
                'event_date': event_date,
                'manager': self.sprint.manager.get_full_name(),
                'sprint': self.sprint,
                'project': self.sprint.project,
                'plan_close_date': plan_close_date,
                'hours': self.sprint.type,
                'target': self.sprint.target,
                'criteria': self.sprint.criteria,
                'extra_hours': self.sprint.extra_hours,
                'reason': self.comment,
                'new_close_date': new_close_date,
                'delay_days': self.sprint.final_delay,
            })

            message_text = Template(message).render(data)

            Telegram(channel=settings.TELEGRAM_MANAGER_CHAT_ID).send(message_text)

            if self.status == self.STATUS_RATED and self.sprint.extra_hours:
                Telegram(channel=settings.TELEGRAM_UPSALE_CHAT_ID).send(message_text)

        if self.status in [self.STATUS_STARTED, self.STATUS_RATED, self.STATUS_CLOSED]:
            template_name = ''
            subject = ''

            email_context = {
                'sprint': self.sprint,
                'date': self.date_create,
                'show_rubedite': self.sprint.manager_id != 1,
                'tasks': self.sprint.tasks.filter(active=True)
            }

            recipients = self.sprint.project.projectRoles.filter(user__email__isnull=False)
            recipients = recipients.values_list('user__email', flat=True)

            if self.status == self.STATUS_STARTED and self.sprint.project.id == 112:
                template_name = 'milestone_started'
                subject = u'{} в проекте {} начат'.format(self.sprint.name, self.sprint.project.name)

            elif self.status == self.STATUS_RATED:
                template_name = 'milestone_rated'
                subject = u'{} в проекте {} оценен'.format(self.sprint.name, self.sprint.project.name)

            elif self.status == self.STATUS_CLOSED and self.sprint.project.id == 112:
                template_name = 'milestone_closed'
                subject = u'{} в проекте {} завершен'.format(self.sprint.name, self.sprint.project.name)
                recipients = [self.sprint.project.payer.email]

            if template_name:
                email_message = EmailMessage(
                    template_name=template_name,
                    subject=subject,
                    context=email_context,
                    attachment_file=self.sprint.file_for_client.path,
                )
                email_message.send_separately(recipients)

        elif self.status == self.STATUS_CLOSE_CONFIRMED and self.sprint.project.id == 112:
            self._send_approve_email_to_devs()

            # send message to payer
            template_name = 'milestone_client_approved'
            subject = u'Вы подтвердили закрытие спринта {} в проекте {}'.format(self.sprint.name, self.sprint.project.name)
            recipients = [self.sprint.project.payer.email]
            email_context = {
                'sprint': self.sprint,
                'date': self.date_create,
                'show_rubedite': self.sprint.manager_id != 1,
                'tasks': self.sprint.tasks.filter(active=True)
            }

            email_message = EmailMessage(
                template_name=template_name,
                subject=subject,
                context=email_context,
            )
            email_message.send_separately(recipients)

    def _send_approve_email_to_devs(self):
        template_name = 'milestone_dev_approve'
        subject = u'{} в проекте {} завершен'.format(self.sprint.name, self.sprint.project.name)

        from PManager.models import Credit
        credits = Credit.objects.filter(milestone=self.sprint, task__isnull=False, type=1)
        developers = credits.values_list('user_id', flat=True)
        for developer in set(developers):
            user = User.objects.get(id=developer)
            email_context = {
                'sprint': self.sprint,
                'date': self.date_create,
                'tasks': self._get_developer_tasks(credits, developer),
                'show_rubedite': self.sprint.manager_id != 1,
            }
            recipients = [user.email]

            email_message = EmailMessage(
                template_name=template_name,
                subject=subject,
                context=email_context,
            )
            email_message.send(recipients)

    @staticmethod
    def _get_developer_tasks(credit_queryset, developer):
        tasks = []
        task_data = {}
        for credit in credit_queryset.filter(user=developer).order_by('task', 'code').select_related('task'):
            task = credit.task
            if task_data and task_data['id'] != task.id:
                tasks.append(task_data)
                task_data = {}

            if credit.code == '1':
                task_data = {
                    'id': task.id,
                    'name': task.name,
                    'credit': credit.value,
                    'charge': 0,
                    'total': credit.value,
                }
            elif credit.code == '2':
                task_data['charge'] = credit.value
                task_data['total'] += credit.value

            tasks.append(task_data)
        return tasks


class PM_MilestoneDevPaymentApproval(models.Model):
    milestone = models.ForeignKey(PM_Milestone, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_approved = models.NullBooleanField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'PManager'
        unique_together = ('milestone', 'user', )


class PM_Task(models.Model):
    MANAGER_ADDITION_PER_BUG = 0.1
    RESP_SUBSTRUCTION_PER_BUG = 0.05
    FEE = 0.1
    MAX_OVERTIME = 3

    bool_choices = (
        ('N', u'No'),
        ('Y', u'Yes'),
    )

    colors = (
        ('grey', u'Серый'),
        ('green', u'Зеленый'),
        ('blue', u'Голубой'),
        ('red', u'Красный'),
        ('yellow', u'Желтый'),
        ('purple', u'Пурпурный'),
        ('orange', u'Оранжевый')
    )

    name = models.CharField(max_length=1000, verbose_name='Заголовок')
    text = models.TextField(validators=[MaxLengthValidator(7000)], verbose_name='Текст СО', blank=True, null=True)
    text_ro = models.TextField(validators=[MaxLengthValidator(7000)], verbose_name='Текст РО', blank=True, null=True)
    text_eo = models.TextField(validators=[MaxLengthValidator(7000)], verbose_name='Текст ЭО', blank=True, null=True)
    number = models.IntegerField()
    project = models.ForeignKey(PM_Project, null=True, blank=True, db_index=True, related_name='projectTasks')
    resp = models.ForeignKey(User, null=True, blank=True, related_name='todo')
    responsible = models.ManyToManyField(User, related_name='hisTasks', null=True, blank=True)
    author = models.ForeignKey(User, related_name='createdTasks', null=True, blank=True)
    lastModifiedBy = models.ForeignKey(User, related_name='modifiedBy', null=True, blank=True)
    status = models.ForeignKey(PM_Task_Status, related_name='tasksByStatus', null=True, blank=True,
                               verbose_name='Статус')
    observers = models.ManyToManyField(User, related_name='tasksLooking', null=True, blank=True)

    perhapsResponsible = models.ManyToManyField(User, related_name='hisTasksMaybe', null=True, blank=True)

    dateCreate = models.DateTimeField(auto_now_add=True, blank=True)
    dateModify = models.DateTimeField(auto_now=True, blank=True)
    dateClose = models.DateTimeField(blank=True, null=True)
    dateStart = models.DateTimeField(blank=True, null=True)
    deadline = models.DateTimeField(blank=True, null=True, verbose_name='Дедлайн')

    milestone = models.ForeignKey(PM_Milestone, related_name='tasks', null=True, blank=True)
    onPlanning = models.BooleanField(blank=True)
    planTime = models.FloatField(blank=True, null=True, default=0)
    planTimeMainOrg = models.FloatField(blank=True, null=True, default=0)
    planTimeRegulator = models.FloatField(blank=True, null=True, default=0)
    realTime = models.BigIntegerField(blank=True, null=True)
    realDateStart = models.DateTimeField(blank=True, null=True)

    closed = models.BooleanField(blank=True, verbose_name='Закрыта')
    started = models.BooleanField(blank=True)
    wasClosed = models.BooleanField(blank=True)
    closedInTime = models.BooleanField(blank=True, default=False)
    public = models.BooleanField(blank=True)
    active = models.BooleanField(default=True, blank=True)

    priority = models.FloatField(default=0.5)
    critically = models.FloatField(default=0.5, verbose_name='Критичность')
    hardness = models.FloatField(default=0.5)
    reconcilement = models.FloatField(default=0.5)
    project_knowledge = models.FloatField(default=0.5)

    parentTask = models.ForeignKey('self', related_name="subTasks", null=True, blank=True, verbose_name='Контейнер')
    tags = generic.GenericRelation(ObjectTags)

    virgin = models.BooleanField(default=True, blank=True)
    viewedUsers = models.ManyToManyField(User, null=True, blank=True)

    files = models.ManyToManyField(PM_Files, related_name="fileTasks", null=True, blank=True)
    files_ro = models.ManyToManyField(PM_Files, related_name="fileTasksRO", null=True, blank=True)
    files_eo = models.ManyToManyField(PM_Files, related_name="fileTasksEO", null=True, blank=True)

    repeatEvery = models.IntegerField(verbose_name=u'Повторите', blank=True, null=True)

    currentTimer = False
    startedTimerExist = False

    color = models.CharField(max_length=100, choices=colors, null=True, blank=True, default='blue')

    release = models.ForeignKey(Release, blank=True, null=True, related_name='tasks')

    isParent = models.BooleanField(default=False, blank=True)

    category = models.OneToOneField(PM_File_Category, on_delete=models.SET_NULL, related_name='category', null=True, blank=True)

    class Meta:
        app_label = 'PManager'

    @property
    def url(self):
        return "/task_detail/?" + (
            ("id=" + str(self.id)) if self.parentTask else ("number=" + str(self.number))) + "&project=" + str(
            self.project.id)

    def safeDelete(self):
        self.active = False
        try:
            PM_File_Category.objects.get(id=self.category_id).delete()
        except:
            pass
        self.save()
        if self.parentTask and self.parentTask.subTasks.filter(active=True).count() == 0:
            self.parentTask.isParent = False
            self.parentTask.save()

    def setIsInTime(self):
        if not self.deadline or self.deadline > timezone.make_aware(datetime.datetime.now(),
                                                                    timezone.get_current_timezone()):
            self.closedInTime = True
        else:
            self.closedInTime = False

    def Close(self, user):
        from django.contrib.contenttypes.models import ContentType

        logger = Logger()

        def increaseTagsForUser(userForTags, tagRelArray):
            for tagRel in tagRelArray:
                tagRelUser = ObjectTags.objects.filter(
                    tag=tagRel.tag,
                    object_id=userForTags.id,
                    content_type=ContentType.objects.get_for_model(user)
                )
                if tagRelUser:
                    tagRelUser = tagRelUser[0]
                else:
                    tagRelUser = ObjectTags(tag=tagRel.tag, content_object=userForTags)

                tagRelUser.weight = int(tagRelUser.weight) + 1
                tagRelUser.save()

        if not self.resp and user:
            self.resp = user

        self.closed = True
        self.critically = 0.5
        self.status = None
        self.onPlanning = False
        self.dateClose = datetime.datetime.now()

        if not self.wasClosed and not self.subTasks.count():
            self.setCreditForTime()
            self.wasClosed = True

        tagRelArray = ObjectTags.objects.filter(
            object_id=self.id,
            content_type=ContentType.objects.get_for_model(PM_Task)
        ).all()

        for ob in self.observers.all():
            if ob.id != self.author.id and (not self.resp or ob.id != self.resp.id):
                increaseTagsForUser(ob, tagRelArray)

        if self.resp and self.author.id != self.resp.id:
            increaseTagsForUser(self.resp, tagRelArray)

        redisSendTaskUpdate({
            'id': self.pk,
            'closed': True
        })
        self.save()

    def setCreditForTime(self):
        from PManager.models import Credit, PM_Achievement, PM_Task_Message, Fee
        import math

        allSum = 0
        allRealTime = 0
        # responsibles real time
        timers = PM_Timer.objects.raw(
            'SELECT SUM(`seconds`) as summ, id, user_id from PManager_pm_timer' +
            ' WHERE `task_id`=' + str(self.id) +
            ' GROUP BY user_id'
        )

        bugsQty = self.messages.filter(bug=True).count()
        for obj in timers:
            ob = {}
            if obj.summ:
                cUser = User.objects.get(pk=int(obj.user_id))
                cUserProf = cUser.get_profile()

                if cUserProf.isEmployee(self.project) and cUser.id != self.author.id and cUser.is_active \
                        and cUserProf.is_outsource:

                    ob['time'] = round(float(obj.summ) / 3600., 2)

                    if self.planTime:
                        if ob['time'] > self.planTime:
                            if (ob['time'] - self.planTime) > self.MAX_OVERTIME:
                                ob['time'] = self.planTime + self.MAX_OVERTIME

                            ob['rating'] = -round(20 * (ob['time'] - self.planTime))
                            accCode = 'rating_minus'
                        else:
                            accCode = 'rating_plus'
                            ob['rating'] = 1
                            if not bugsQty:
                                ob['rating'] += 1

                        if accCode:
                            try:
                                acc = PM_Achievement.objects.get(code=accCode)
                                acc.addToUser(cUser)
                            except PM_Achievement.DoesNotExist:
                                pass

                    curUserRating = ob.get('rating', 0)

                    # set user rating
                    profResp = cUser.get_profile()
                    respFine = profResp.getFine()
                    if curUserRating != 0 and profResp.is_outsource:
                        obRating = None

                        if curUserRating < 0:
                            obRating = FineHistory(value=curUserRating, user=cUser)
                        elif curUserRating > 0:
                            if respFine < 0:
                                if -respFine >= curUserRating:
                                    obRating = FineHistory(value=curUserRating, user=cUser)
                                else:
                                    obRating = FineHistory(value=-respFine, user=cUser)
                                    ratingLeft = curUserRating + respFine

                                    if ratingLeft:
                                        ratingLeft = RatingHistory(value=ratingLeft, user=cUser)
                                        ratingLeft.save()
                            else:
                                obRating = RatingHistory(value=curUserRating, user=cUser)

                        if obRating:
                            obRating.save()

                    if ob['time']:
                        allRealTime += ob['time']

                        userBet = profResp.getBet(self.project)
                        if userBet:
                            curPrice = userBet * float(ob['time'])

                            if curPrice:
                                substruction = 0
                                if bugsQty:
                                    substruction = round(curPrice * self.RESP_SUBSTRUCTION_PER_BUG * bugsQty)
                                    curPrice -= substruction

                                allSum = allSum + curPrice

                                respFine = profResp.getFine()
                                fineSum = 0
                                if respFine:
                                    fineSum = - respFine * float(ob['time'])
                                    fee = Fee(
                                        user=profResp.user,
                                        value=fineSum,
                                        project=self.project,
                                        task=self
                                    )
                                    fee.save()

                                feeValue = math.floor(curPrice * self.FEE)

                                fee = Fee(
                                    user=profResp.user,
                                    value=feeValue,
                                    project=self.project,
                                    task=self
                                )
                                fee.save()

                                credit = Credit(
                                    user=profResp.user,
                                    value=curPrice - feeValue - fineSum,
                                    project=self.project,
                                    task=self,
                                    type='Resp real time',
                                    comment=(
                                                    ('+' if curUserRating >= 0 else '') + str(
                                                curUserRating) + u' к рейтингу') +
                                            ((' -' + str(substruction) + u' за ошибки') if substruction else u'')
                                )
                                credit.save()

        if allRealTime or self.planTime:
            if self.planTime:
                managers = PM_ProjectRoles.objects.filter(
                    project=self.project,
                    role__code='manager',
                    user__in=self.observers.all()
                )

                cManagers = 0
                aManagers = []
                for manager in managers:
                    if manager.user.get_profile().is_heliard_manager:
                        bet = manager.user.get_profile().getBet(self.project, None, manager.role.code)
                        if bet:
                            cManagers += 1
                            setattr(manager, 'bet', bet)
                            aManagers.append(manager)

                for manager in aManagers:
                    curTime = self.planTime * 1.0 / cManagers

                    if curTime:
                        bugQty = PM_Task_Message.objects.filter(author=manager, bug=True, task=self).count()
                        if bugQty:
                            curTime += curTime * self.MANAGER_ADDITION_PER_BUG * bugQty

                        bet = manager.user.get_profile().heliard_manager_rate
                        if bet:
                            price = bet * float(curTime)
                            if price:
                                credit = Credit(
                                    user=manager.user,
                                    value=price,
                                    project=self.project,
                                    task=self,
                                    type='Manager with bet'
                                )
                                credit.save()

                                allSum = allSum + price

            if allSum:
                # client
                clientComission = int(self.project.getSettings().get('client_comission', 0) or COMISSION)
                clientFeeSum = math.floor(allSum * clientComission / 100)

                if self.project.payer:
                    credit = Credit(
                        user=self.project.payer,
                        value=-allSum - clientFeeSum,
                        project=self.project,
                        task=self,
                        type='Client with comission'
                    )
                    credit.save()

                    if clientFeeSum:
                        fee = Fee(
                            user=self.project.payer,
                            value=clientFeeSum,
                            project=self.project,
                            task=self
                        )
                        fee.save()

    def Open(self):
        self.closed = False
        self.dateClose = None

        redisSendTaskUpdate({
            'id': self.pk,
            'closed': False
        })

        self.save()

    def Start(self):
        if not self.realDateStart:  # если до этого еще не была запущена
            self.realDateStart = datetime.datetime.now()  # заносим дату запуска
        self.started = True
        self.virgin = False
        self.save()

    def Stop(self):
        self.started = False
        self.save()

    def setPlanTime(self, val, request):
        from PManager.models.scrum import PM_MilestoneChanges
        if request.user.is_authenticated():
            if not self.onPlanning and self.canPMUserSetPlanTime(request.user.get_profile()):
                oldPlanTime = self.planTime or 0

                self.planTime = float(val)
                self.save()

                if self.milestone and oldPlanTime != self.planTime:
                    change = PM_MilestoneChanges(milestone=self.milestone, value=(self.planTime - oldPlanTime))
                    change.save()
            else:
                planTime, created = PM_User_PlanTime.objects.get_or_create(user=request.user, task=self)
                planTime.time = float(val)
                planTime.save()

        redisSendTaskUpdate({
            'id': self.pk,
            'planTime': self.planTime if self.onPlanning else float(val)
        })

    def saveTaskTags(self):
        textManager = trackMorphy()

        tags = textManager.parseTags(self.name + u' ' + self.text)

        for k, tagInfo in tags.iteritems():

            tagId, created = Tags.objects.get_or_create(tagText=tagInfo["norm"])

            if tagId.id > 0:
                tagObject, created = ObjectTags.objects.get_or_create(
                    tag=tagId,
                    object_id=self.id,
                    content_type=ContentType.objects.get_for_model(PM_Task)
                )

                tagObject.weight = int(tagInfo['weight'])
                tagObject.content_object = self

                tagObject.save()

    def startTimer(self, user):
        if not self.currentTimer:
            try:
                self.currentTimer = PM_Timer.objects.get(task=self, dateEnd=None)
            except PM_Timer.DoesNotExist:
                self.currentTimer = PM_Timer(task=self, user=user, dateStart=datetime.datetime.now())
                self.currentTimer.save()

        redisSendTaskUpdate({
            'id': self.pk,
            'started': True,
            'startedTimerExist': True,
            'eventAuthor': self.currentTimer.user.id,
            'name': self.name,
            'url': self.url
        })

    def endTimer(self, user=None, comment=None):
        logger = Logger()

        if not self.currentTimer:
            try:
                self.currentTimer = PM_Timer.objects.get(task=self, dateEnd=None)
            except PM_Timer.DoesNotExist:
                return

        if self.currentTimer:
            user_id = self.currentTimer.user.id
            if not comment:
                self.currentTimer.delete()
            else:
                self.currentTimer.dateEnd = datetime.datetime.now()
                self.currentTimer.comment = comment
                delta = timezone.make_aware(self.currentTimer.dateEnd,
                                            timezone.get_default_timezone()) - self.currentTimer.dateStart
                self.currentTimer.seconds = delta.total_seconds()

                self.currentTimer.save()
                if not self.realTime: self.realTime = 0
                self.realTime = int(self.realTime)
                self.realTime = self.realTime + delta.seconds

                logger.log(self.currentTimer.user, 'DAILY_TIME', delta.seconds, self.project.id)

            redisSendTaskUpdate({
                'id': self.pk,
                'started': False,
                'startedTimerExist': False,
                'eventAuthor': user_id
            })
            self.save()

        return self

    @staticmethod
    def getAllTimeOfTasksWithSubtasks(aId):
        if not aId:
            return

        aTime = PM_Timer.getSumsOfTasks(aId)
        aTasksId = aTime.keys()
        timers = PM_Timer.objects.filter(
            Q(Q(task__in=aTasksId) | Q(task__parentTask_id__in=aTasksId)), dateEnd__isnull=True, dateStart__isnull=False
        ).values('dateStart', 'task_id', 'user_id', 'task__parentTask_id')
        now = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone())

        for t in timers:
            delta = now - t['dateStart']
            aCurObj = aTime[t['task__parentTask_id']] if 'task__parentTask_id' in t and t[
                'task__parentTask_id'] in aTime else \
                aTime[t['task_id']]
            if t['user_id'] not in aCurObj:
                aCurObj[t['user_id']] = 0

            aCurObj[t['user_id']] += delta.seconds

        return aTime

    def getAllTime(self):
        aTime = PM_Timer.getSumsOfTasks([self.id])
        return sum(aTime[self.id].values()) if self.id in aTime else 0

    def canPMUserView(self, pm_user):
        return pm_user.hasAccess(self, 'view')

    def canPMUserRemove(self, pm_user):
        if self.realDateStart:
            return False

        return pm_user.isManager(self.project) or (self.author and pm_user.user.id == self.author.id)

    def canPMUserSetPlanTime(self, pm_user):
        return (not self.planTime and pm_user.isManager(self.project)) or not self.realDateStart and (
                pm_user.isManager(self.project) or
                int(self.author.id) == int(pm_user.user.id) or
                self.onPlanning or (
                    # is responsible and planTime is empty
                        hasattr(self.resp, 'id') and int(self.resp.id) == int(pm_user.user.id) and
                        (not self.planTime or self.status and self.status.code == 'not_approved')
                )
        )

    def setChangedForUsers(self, user=None):
        self.viewedUsers.clear()
        if user and isinstance(user, User):
            self.viewedUsers.add(user)

    def isViewed(self, user):
        return user.id in [u.id for u in self.viewedUsers.all()]

    def createTaskContainer(self, user=None):
        container = PM_Task(
            name=self.name,
            project=self.project,
            author=self.author,
            dateCreate=self.dateCreate,
            # deadline=self.deadline,
            planTime=self.planTime,
            critically=self.critically,
            hardness=self.hardness,
            reconcilement=self.reconcilement,
            project_knowledge=self.project_knowledge,
            active=True
        )
        container.save()
        self.setParent(container.id)
        if user:
            container.setChangedForUsers(user)
        return container

    @staticmethod
    def createByString(taskName, currentUser, uploadedFiles, parent=None, project=None):
        import re
        from PManager.models.users import PM_User

        arTags = {
            u'для ': 'responsible',
            u' до ': 'deadline',
            u'примерно ': 'about',
            u' файл ': 'file',
            u' от ': 'from'
        }

        # TODO: сделать обработку быстрых тегов
        arSaveFields = {}

        if project:
            arSaveFields['project'] = project

        arFiles = []

        if uploadedFiles:
            uploadedFiles = PM_Files.objects.filter(pk__in=uploadedFiles)
            for file in uploadedFiles:
                arFiles.append(file)

        resp = None
        if len(taskName) > 0:
            if taskName[-1] == u'!':
                taskName = taskName[:-1]
                arSaveFields['critically'] = 0.75

            for tagname, tag in arTags.iteritems():
                aritems = taskName.split(tagname)
                i = 0
                for tagSpliced in aritems:
                    i += 1
                    if tagSpliced[0] == '#':
                        tagSpliced = tagSpliced[1:tagSpliced.find('#', 1)]

                        if tag == 'responsible':
                            resp = PM_User.getOrCreateByEmail(tagSpliced, arSaveFields['project'], 'employee')

                        elif tag == 'deadline':
                            def dateFromTag(tag):
                                return {
                                    'today': datetime.datetime.today(),
                                    'tomorrow': datetime.datetime.today() + datetime.timedelta(days=1),
                                    'aftertomorrow': datetime.datetime.today() + datetime.timedelta(days=2),
                                    'week': datetime.datetime.today() + datetime.timedelta(days=7)
                                }.get(tag, None)

                            arSaveFields['deadline'] = dateFromTag(tagSpliced)
                        elif tag == 'about':
                            arSaveFields['planTime'] = int(tagSpliced)

                        elif tag == 'file':
                            file = PM_Files.objects.get(id=tagSpliced)
                            if file.id:
                                arFiles.append(file)

                        elif tag == 'from':
                            arSaveFields['author'] = PM_User.getOrCreateByEmail(tagSpliced, arSaveFields['project'],
                                                                                'client')

            for tagname, tag in arTags.iteritems():
                myRe = re.compile(tagname + ur'\#([^\#]+)\#', re.UNICODE)
                taskName = myRe.sub('', taskName).strip()

            taskName = taskName.split('///')
            arSaveFields['text'] = taskName[1] if len(taskName) > 1 else ''
            arSaveFields['name'] = taskName[0][:300] + "..." if (len(taskName) > 300) else taskName[0]

            if parent:
                try:
                    parentTask = PM_Task.objects.get(id=parent, active=True)
                    parentTask.isParent = True
                    parentTask.save()

                    qtySubtasks = parentTask.subTasks.filter(active=True).count()

                    if qtySubtasks == 0 and parentTask.realDateStart:
                        try:
                            curUserObj = User.objects.get(pk=currentUser.id)
                            arSaveFields['parentTask'] = parentTask.createTaskContainer(
                                curUserObj
                            )
                        except User.DoesNotExist:
                            return False

                    else:
                        arSaveFields['parentTask'] = parentTask

                except PM_Task.DoesNotExist:
                    pass

        if "author" not in arSaveFields:
            arSaveFields["author"] = currentUser

        task = PM_Task(**arSaveFields)

        if resp:
            task.resp = resp

            # если у юзера нет ролей в текущем проекте, назначаем его разработчиком
            if not resp.get_profile().hasRole(task.project, not_guest=True):
                resp.get_profile().setRole('employee', task.project)
                if resp.get_profile().is_outsource:
                    from PManager.models.agreements import Agreement
                    Agreement.objects.get_or_create(payer=task.project.payer, resp=resp)
                    # elif task.parentTask:
                    #     for resp in task.parentTask.responsible.all():
                    #         task.responsible.add(resp) #17.04.2014 task #553

        task.lastModifiedBy = currentUser

        task.save()

        for file in arFiles:
            task.files.add(file)

        task.observers.add(task.author)

        PM_Task.saveTaskTags(task)

        task.setChangedForUsers(currentUser)
        arEmail = []
        if task.resp:
            arEmail.append(task.resp.email if task.resp.email is not currentUser.email else None)

            task.sendTaskEmail('new_task', arEmail)

        return task

    def sendTaskEmail(self, type, arEmail, title=''):
        taskdata = {
            'task_url': self.url,
            'name': self.name,
            'text': self.text if self.text != self.name else '',
            'dateCreate': timezone.make_aware(datetime.datetime.now(), timezone.get_current_timezone()),
            'time': unicode(self.currentTimer),
            'author': self.author
        }

        sendMes = EmailMessage(type,
                               {
                                   'task': taskdata
                               },
                               (title if title else 'Вас назначили ответственным в новой задаче!')
                               )

        try:
            sendMes.send(arEmail)
        except Exception:
            print 'Message is not sent'

    def getPrice(self, profile):
        bet = profile.getBet(self.project)

        if profile.isClient(self.project):
            pass
        elif profile.isEmployee(self.project):
            pass

    # should be removed, since deprecated
    @staticmethod
    def getListPrepare(tasks, add_tasks, join_project_name=False):
        from PManager.services.task_list import task_list_prepare
        return task_list_prepare(tasks, add_tasks, join_project_name)

    @staticmethod
    def getQtyForUser(user, project=None, addFilter={}):
        filterForUser = PM_Task.getQArgsFilterForUser(user, project)
        if project:
            filterForUser.append(Q(project=project))

        filterForUser.append(Q(**addFilter))
        try:
            return PM_Task.objects.filter(*filterForUser).distinct().count()
        except ValueError:
            return 0

    @staticmethod
    def getQArgsFilterForUser(user, project=None):
        from django.db.models import Count

        filterQArgs = []
        pm_user = user.get_profile()
        bExist = False
        if project:
            if pm_user.isManager(project):
                bExist = True
            elif pm_user.isEmployee(project):
                subtasksSubQuery = PM_Task.objects.exclude(parentTask__isnull=True) \
                    .filter(resp=user, closed=False).values('parentTask__id') \
                    .annotate(dcount=Count('parentTask__id'))
                aExternalId = []
                for obj in subtasksSubQuery:
                    aExternalId.append(obj['parentTask__id'])

                filterQArgs.append((
                        Q(onPlanning=True) | Q(author=user) | Q(resp=user) | Q(observers=user) | Q(
                    id__in=aExternalId)
                ))
                bExist = True
            elif pm_user.isGuest(project):
                filterQArgs.append(Q(observers=user))
                bExist = True

        if not bExist:
            # userProjects = user.get_profile().getProjects()
            mProjects = user.get_profile().managedProjects
            q = Q(author=user) | Q(resp=user) | Q(observers=user) | Q(project__in=mProjects)

            filterQArgs.append(
                Q(q)
            )

        return filterQArgs

    @staticmethod
    def mergeFilterObjAndArray(obj, arr):
        for (k, v) in obj.iteritems():
            arr.append(Q(**{k: v}))
        return arr

    @staticmethod
    def getForUser(user, project, filter={}, filterQArgs=[], arOrderParams={}):
        from django.db.models import Count

        order_by = arOrderParams.get('order_by', 'closed')

        pm_user = user.get_profile()

        if not pm_user:
            raise Exception('Access denied')

        if 'id' in filter or 'pk' in filter:
            filter = {
                'id': filter['id'] if 'id' in filter else filter['pk']
            }
            filterQArgs = []

        if not 'parentTask' in filter:
            filterQArgs += PM_Task.getQArgsFilterForUser(user, project)

        excludeFilter = {}
        if 'exclude' in filter:
            excludeFilter = filter['exclude']
            del filter['exclude']

        filter['active'] = True

        # subtasks search
        if filter and not 'isParent' in filter and \
                not 'parentTask' in filter and \
                not 'id' in filter and not 'onlyParent' in arOrderParams:

            filterSubtasks = filter.copy()
            filterSubtasks['parentTask__isnull'] = False
            filterSubtasks['parentTask__active'] = True
            try:
                subTasks = PM_Task.objects.filter(*filterQArgs, **filterSubtasks).values('parentTask__id').annotate(
                    dcount=Count('parentTask__id'))

                subTasks2 = []
                if subTasks:
                    subTasks2 = PM_Task.objects.filter(id__in=[subtask['parentTask__id'] for subtask in subTasks])\
                        .values('parentTask__id').annotate(
                            dcount=Count('parentTask__id'))

                subTasks3 = []
                if subTasks2:
                    subTasks3 = PM_Task.objects.filter(id__in=[subtask['parentTask__id'] for subtask in subTasks2])\
                        .values('parentTask__id').annotate(
                        dcount=Count('parentTask__id'))

            except ValueError:
                subTasks = []
                subTasks2 = []
                subTasks3 = []

            aTasksIdFromSubTasks = [subtask['parentTask__id'] for subtask in (list(subTasks) + list(subTasks2) + list(subTasks3))]
        else:
            aTasksIdFromSubTasks = None

        #todo: добавить бесконечный подъем вверх

        filterQArgs = PM_Task.mergeFilterObjAndArray(filter, filterQArgs)

        if aTasksIdFromSubTasks:
            filterQArgs = [Q(*filterQArgs) | Q(
                Q(id__in=aTasksIdFromSubTasks) & Q(parentTask__isnull=True))]  # old conditions array | ID of parent tasks of match subtasks

            filter = {}

        try:
            tasks = PM_Task.objects.filter(*filterQArgs, **filter).exclude(project__closed=True,
                                                                           project__locked=True).distinct()
        except ValueError:
            tasks = None

        if arOrderParams.get('group') == 'milestones':
            order = ['-milestone__date', '-milestone__id']
        else:
            order = []

        if type(order_by) == type([]):
            for i in order_by:
                order.append(i)
        else:
            order.append(order_by)

        order.append('-started')
        order.append('-critically')
        order.append('-dateStart')
        order.append('-dateClose')
        order.append('-number')
        if tasks is not None:
            tasks = tasks.order_by(*order)
            if excludeFilter:
                tasks = tasks.exclude(**excludeFilter)

            tasks = tasks.order_by(*order)

        return {
            'tasks': tasks,
            'filter': filterQArgs
        }

    @staticmethod
    def getSimilar(text, project):
        SIMILARITY_PERCENT = 40

        def sortByTagsCount(task):
            return task.tagSimilarCount

        textManager = trackMorphy()

        parsedTags = textManager.parseTags(text)

        arText = []
        for k, tagInfo in parsedTags.iteritems():
            arText.append(tagInfo["norm"])

        min_similar_words = len(arText) * SIMILARITY_PERCENT / 100
        arTasks = []

        if arText:
            tags = Tags.objects.filter(tagText__in=arText)
            if tags.count() > 1:
                tasks = PM_Task.objects.filter(project=project, tags__tag__in=tags, active=True).distinct()
                for task in tasks:
                    iSimilarTagCount = task.tags.filter(tag__in=tags).count()
                    if iSimilarTagCount > min_similar_words:
                        setattr(task, 'tagSimilarCount', iSimilarTagCount)
                        arTasks.append(task)
                arTasks.sort(key=sortByTagsCount, reverse=True)

        return arTasks

    # deprecated, since brought by merge from another branch, something is changed?
    # see PManager.services.rating.get_user_quality_for_task
    def getUserQuality(self, userId):
        taskTagRelArray = ObjectTags.objects.filter(object_id=self.id,
                                                    content_type=ContentType.objects.get_for_model(self))

        arTagsId = [str(tagRel.tag.id) for tagRel in taskTagRelArray]

        userTagSums = {}
        if len(arTagsId) > 0:
            for obj1 in ObjectTags.objects.raw(
                    'SELECT SUM(`weight`) as weight_sum, `id`, `object_id`, `content_type_id`' +
                    ' from PManager_objecttags WHERE' +
                    ' tag_id in (' + ', '.join(arTagsId) + ')' +
                    ' AND content_type_id=' + str(ContentType.objects.get_for_model(User).id) +
                    ' GROUP BY object_id'):
                if obj1.content_object:
                    userTagSums[str(obj1.content_object.id)] = int(obj1.weight_sum)

            minTagCount, maxTagCount = False, 0

            for userId in userTagSums:
                if maxTagCount < userTagSums[userId]: maxTagCount = userTagSums[userId]
                if minTagCount > userTagSums[userId] or minTagCount == False: minTagCount = userTagSums[userId]

            currentRecommendedUser = None
            if maxTagCount > 0:
                for userId in userTagSums:
                    if minTagCount == maxTagCount:
                        userTagSums[userId] = 1 if userTagSums[userId] == minTagCount else 0
                    else:
                        userTagSums[userId] = float((int(userTagSums[userId]) - int(minTagCount))) / float(
                            (int(maxTagCount) - int(minTagCount)))
            return userTagSums[userId] if userId in userTagSums else 0
        return 0

    def getUsersEmail(self, excludeUsers=None):
        if not excludeUsers:
            excludeUsers = []

        arEmail = []
        if self.author and self.author.is_active and self.author.id not in excludeUsers:
            if self.author.email:
                arEmail.append(self.author.email)
            else:
                arEmail.append(self.author.username)

        if self.resp:
            if self.resp.id not in excludeUsers and self.resp.is_active:
                if self.resp.email:
                    arEmail.append(self.resp.email)
                else:
                    arEmail.append(self.resp.username)

        if not isinstance(self.observers, list):
            observers = self.observers.all()
        else:
            observers = self.observers

        for resp in observers:
            if resp.id not in excludeUsers and resp.is_active:
                if resp.email:
                    arEmail.append(resp.email)
                else:
                    arEmail.append(resp.username)

        return arEmail

    def setStatus(self, status):
        try:
            self.status = PM_Task_Status.objects.get(code=status)
            self.save()
        except PM_Task_Status.DoesNotExist:
            pass

    def setParent(self, taskId):
        try:
            parent = None
            if taskId and int(taskId) > 0:
                parent = PM_Task.objects.get(id=int(taskId), parentTask__isnull=True)
                lastSubTask = parent.subTasks.order_by('-number')
                parent.isParent = True
                parent.save()
            else:
                lastSubTask = PM_Task.objects.filter(project=self.project, parentTask__isnull=True).order_by('-number')

            lastNumber = 0
            if lastSubTask.count() and lastSubTask[0]:
                lastNumber = lastSubTask[0].number

            for task in self.subTasks.all():
                task.setParent(parent.id if parent else 0)

            self.number = lastNumber + 1
            self.parentTask = parent
            self.save()

            return self.number
        except PM_Task.DoesNotExist:
            return False

    # deprecated, since brought by merge from another branch, something is changed?
    # see PManager.services.rating.get_user_rating_for_task
    def getUserRating(self, user):
        assert user.id > 0

        userTagSums = {}
        taskTagRelArray = ObjectTags.objects.filter(object_id=self.id,
                                                    content_type=ContentType.objects.get_for_model(self))

        arTagsId = [str(tagRel.tag.id) for tagRel in taskTagRelArray]

        if len(arTagsId) > 0:
            for obj1 in ObjectTags.objects.raw(
                    'SELECT SUM(`weight`) as weight_sum, `id`, `object_id`, `content_type_id` from PManager_objecttags WHERE tag_id in (' + ', '.join(
                        arTagsId) + ') AND object_id=' + str(
                        user.id) + ' AND content_type_id=' + str(
                        ContentType.objects.get_for_model(User).id) + ' GROUP BY object_id'):
                if obj1.content_object:
                    userTagSums[str(obj1.content_object.id)] = int(obj1.weight_sum)

            return userTagSums.get(str(user.id), 0)
        return 0

    def systemMessage(self, text, user=None, code=None):
        message = PM_Task_Message(text=text, task=self, author=user, isSystemLog=True, code=code)
        message.save()
        redisSendLogMessage(message.getJson({
            'noveltyMark': True,
            'onlyForUsers': [message.author.id] + ([message.userTo.id] if message.userTo else [])
            if message.hidden else
            (
                [u.id for u in message.task.observers.all()] +
                [message.author.id] +
                [message.userTo.id] if message.userTo else [] +
                                                           [self.author.id] +
                                                           [self.resp.id] if self.resp else [] +
                                                                                            [r['user__id'] for r in
                                                                                             PM_ProjectRoles.objects.filter(
                                                                                                 project=self.project,
                                                                                                 role__code='manager'
                                                                                             ).values('user__id')]
            )
        }))

    def canEdit(self, user):
        return (
                (self.author and self.author.id == user.id)
                or
                (self.resp and user.id == self.resp.id)
                or
                (self.project and user.get_profile().isManager(self.project))
        )

    @property
    def is_task_added_after_sprint_rated(self):
        sprint_rate_status = PM_MilestoneStatus.objects.filter(
            sprint=self.milestone,
            status=PM_MilestoneStatus.STATUS_RATED
        )
        sprint_rate_status = sprint_rate_status.order_by('date_create')
        if self.dateCreate and len(sprint_rate_status):
            sprint_rate_date = sprint_rate_status[0].date_create
            return self.dateCreate > sprint_rate_date
        else:
            return False

    def save(self, *args, **kwargs):
        self.dateModify = datetime.datetime.now()
        if not self.project:
            if self.author:
                roles = self.author.projectRoles.all()[:1]
                if roles and roles[0] and roles[0].project:
                    self.project = roles[0].project

        # if task is new, add number
        if not self.id:
            try:
                lastTaskInProject = PM_Task.objects.filter(project=self.project).order_by('-number')
                if self.parentTask:
                    lastTaskInProject = lastTaskInProject.filter(parentTask=self.parentTask)
                else:
                    lastTaskInProject = lastTaskInProject.filter(parentTask__isnull=True)

                lastTaskInProject = lastTaskInProject[0]

                self.number = int(lastTaskInProject.number) + 1 if lastTaskInProject.number else 1
            except:
                self.number = 1


        super(self.__class__, self).save(*args, **kwargs)

    def __str__(self):
        return (unicode(self.parentTask.name) + ' / ' if self.parentTask else '') + unicode(self.name)

    def __unicode__(self):
        return (unicode(self.parentTask.name) + ' / ' if self.parentTask else '') + unicode(self.name)


class PM_Timer(models.Model):
    task = models.ForeignKey(PM_Task, db_index=True)
    dateStart = models.DateTimeField(auto_now_add=True, blank=True)
    dateEnd = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey(User, db_index=True)
    seconds = models.BigIntegerField(blank=True, null=True)
    comment = models.CharField(max_length=1000, blank=True, null=True)
    price = models.FloatField(blank=True, null=True)

    def __unicode__(self):
        timeTimer = self.getTime()
        if timeTimer['hours'] < 10: timeTimer['hours'] = u'0' + unicode(timeTimer['hours'])
        if timeTimer['minutes'] < 10: timeTimer['minutes'] = u'0' + unicode(timeTimer['minutes'])
        if timeTimer['seconds'] < 10: timeTimer['seconds'] = u'0' + unicode(timeTimer['seconds'])

        return unicode(timeTimer['hours']) + u':' + unicode(timeTimer['minutes']) + u':' + unicode(timeTimer['seconds'])

    def getTime(self):
        dateEnd = timezone.make_aware(datetime.datetime.now(),
                                      timezone.get_current_timezone()) if not self.dateEnd else self.dateEnd
        delta = None
        if self.seconds:
            delta = datetime.timedelta(seconds=int(self.seconds))
        else:
            try:
                delta = dateEnd - self.dateStart
            except TypeError:
                # if dateEnd is recently appended (not received from DB)
                if not timezone.is_aware(dateEnd):
                    dateEnd = timezone.make_aware(dateEnd, timezone.get_current_timezone())
                if self.dateStart:
                    delta = dateEnd - self.dateStart

        objTime = templateTools.dateTime.timeFromTimestamp(delta.total_seconds())

        return objTime

    @staticmethod
    def getSumsOfTasks(aTaskId):
        if not aTaskId:
            return

        timers = PM_Timer.objects.filter(task_id__in=aTaskId).values('task_id', 'user_id').annotate(summ=Sum('seconds'))
        allTime = {}
        for timer in timers:
            if timer['task_id'] not in allTime:
                allTime[timer['task_id']] = {}

            allTime[timer['task_id']][timer['user_id']] = timer['summ'] if timer['summ'] else 0

        aSubtasksByTask = dict()
        subTasks = PM_Task.objects.filter(parentTask__in=aTaskId, virgin=False, active=True).values('id',
                                                                                                    'parentTask_id')

        for s in subTasks:
            if s['parentTask_id'] not in aSubtasksByTask:
                aSubtasksByTask[s['parentTask_id']] = []

            aSubtasksByTask[s['parentTask_id']].append(s['id'])

        for taskId in aSubtasksByTask:
            if not taskId in allTime:
                allTime[taskId] = {}
            timers = PM_Timer.objects.filter(task_id__in=aSubtasksByTask[taskId]).values('task_id', 'user_id').annotate(
                summ=Sum('seconds'))
            for t in timers:
                if t['user_id'] not in allTime[taskId]:
                    allTime[taskId][t['user_id']] = 0

                allTime[taskId][t['user_id']] += t['summ'] if t['summ'] else 0

        return allTime

    class Meta:
        app_label = 'PManager'


class PM_Properties(models.Model):
    code = models.CharField(max_length=255, null=True)
    name = models.CharField(max_length=255)

    class Meta:
        app_label = 'PManager'


class PM_Property_Values(models.Model):
    propertyId = models.ForeignKey(PM_Properties)
    value = models.CharField(max_length=1000)
    taskId = models.ForeignKey(PM_Task)

    class Meta:
        app_label = 'PManager'


class PM_Task_Message(models.Model):
    TAB_CHOICES = (
        ('SO', "СО"),
        ('RO', "РО"),
        ('EO', "ЭО"),
    )

    text = models.CharField(max_length=10000)
    type = models.CharField(max_length=3, null=True, blank=True)
    author = models.ForeignKey(User, related_name="outputMessages", null=True, blank=True, db_index=True)
    dateCreate = models.DateTimeField(auto_now_add=True, blank=True)
    dateModify = models.DateTimeField(auto_now=True, blank=True, null=True)
    modifiedBy = models.ForeignKey(User, null=True, blank=True)
    task = models.ForeignKey(PM_Task, null=True, related_name="messages", db_index=True)
    project = models.ForeignKey(PM_Project, null=True, db_index=True)
    commit = models.CharField(max_length=42, null=True, blank=True)
    userTo = models.ForeignKey(User, null=True, related_name="incomingMessages", blank=True, db_index=True)
    files = models.ManyToManyField(PM_Files, related_name="msgTasks", null=True, blank=True)
    filesExist = models.BooleanField(default=False, db_index=True)
    hidden = models.BooleanField(default=False)
    hidden_from_clients = models.BooleanField(default=False)
    hidden_from_employee = models.BooleanField(default=False)
    isSystemLog = models.BooleanField(blank=True)
    code = models.CharField(max_length=255, null=True, blank=True)
    read = models.BooleanField(blank=True)
    todo = models.BooleanField(blank=True, db_index=True)
    checked = models.BooleanField(blank=True, db_index=True)
    bug = models.BooleanField(blank=True, db_index=True)
    solution = models.BooleanField(default=False)
    requested_time = models.IntegerField(blank=True, null=True)
    requested_time_approved = models.BooleanField(default=False)
    requested_time_approved_by = models.ForeignKey(User, null=True, blank=True, related_name="approvedTimeRequests")
    requested_time_approve_date = models.DateTimeField(blank=True, null=True)

    # tab = models.CharField(default="SO", choices=TAB_CHOICES, max_length=2)  # for division comments by tabs

    def __unicode__(self):
        return self.text

    def save(self, *args, **kwargs):
        if not self.project and self.task:
            if not isinstance(self.task, PM_Task):
                try:
                    self.task = PM_Task.objects.get(pk=self.task)
                except PM_Task.DoesNotExist:
                    return False

            self.project = self.task.project

        super(self.__class__, self).save(*args, **kwargs)

    @classmethod
    def create_commit_message(cls, df, author, task):

        return cls.objects.create(text=df.message,
                                  author=author,
                                  task=task,
                                  commit=df.hash,
                                  project=task.project,
                                  code="GIT_COMMIT"
                                  )

    def updateFromRequestData(self, data, user):
        changed = False
        if 'checked' in data and self.checked != bool(int(data['checked'])):
            self.checked = bool(int(data['checked']))
            changed = True

        if self.canEdit(user):
            if 'todo' in data and self.todo != bool(int(data['todo'])):
                self.todo = bool(int(data['todo']))
                changed = True
            if 'bug' in data and self.bug != bool(int(data['bug'])):
                self.bug = bool(int(data['bug']))
                changed = True
            if 'hidden_from_employee' in data:
                r = not not data['hidden_from_employee']
                if self.hidden_from_employee != r:
                    self.hidden_from_employee = r
                    changed = True
            if 'hidden_from_clients' in data:
                r = bool(data['hidden_from_clients'])
                if self.hidden_from_clients != r:
                    self.hidden_from_clients = r
                    changed = True

            if 'text' in data and not changed:
                self.text = data['text']
                changed = True

            if 'task' in data:
                try:
                    self.task = PM_Task.objects.get(pk=int(data['task']))
                    changed = True
                except (PM_Task.DoesNotExist, TypeError):
                    pass

        return changed

    def getJson(self, addParams=None, cur_user=None):
        from PManager.viewsExt.tools import taskExtensions
        from PManager.templatetags.thumbnail import thumbnail

        if not addParams:
            addParams = {}

        profileAuthor = self.author.get_profile() if self.author else None
        cur_profile = cur_user.get_profile() if cur_user else None
        if self.code == 'SET_PLAN_TIME' and cur_profile:
            if self.task.onPlanning and cur_profile.id != profileAuthor.id:
                p = self.task.project

                if cur_profile and (
                        cur_profile.user.id == self.project.payer.id
                        or
                        cur_profile.isEmployee(p)
                ):
                    try:
                        planTime = PM_User_PlanTime.objects.get(
                            user=self.author,
                            task=self.task
                        )

                        if profileAuthor.isEmployee(p):
                            bet = cur_profile.getBet(self.project, None, 'client') \
                                  or self.author.get_profile().getBet(self.project, None, 'employee')

                        elif profileAuthor.isClient(p):
                            bet = cur_profile.getBet(self.project, None, 'employee') \
                                  or self.author.get_profile().getBet(self.project, None, 'client')

                        else:
                            bet = cur_profile.getBet(self.project) \
                                  or self.author.get_profile().getBet(self.project)

                        addParams.update({
                            'confirmation': (
                                    '<div>'
                                    '<p>Стоимость задачи составит <b>' + str(planTime.time * bet) + ' руб.</b></p>'
                                                                                                    '<a class="button orange-button" href="' + self.task.url + '&confirm=' + str(
                                self.id) + '" ' +
                                    '" class="js-confirm-estimate agree-with-button">Выбрать исполнителем</a></div>'
                            )
                        })

                    except PM_User_PlanTime.DoesNotExist:
                        pass

        elif self.code == 'TIME_REQUEST':
            if not self.requested_time_approved:
                if cur_profile and (
                        cur_profile.user.id == self.project.payer.id or cur_profile.isManager(self.project)):
                    addParams.update({
                        'confirmation': (
                                '<div class="message-desc-right"><a class="button green-button" href="' + self.task.url + '&confirm=' + str(
                            self.id) + '" ' +
                                '" class="js-confirm-estimate agree-with-button" style="line-height: 24px">Добавить сумму: ' + str(
                            self.requested_time) + ' руб.</a></div>'
                        )
                    })
            else:
                addParams.update({
                    'confirmation': (
                            u'<div class="message-desc-right">' +
                            unicode(
                                self.requested_time_approved_by.last_name + ' ' + self.requested_time_approved_by.first_name if
                                self.requested_time_approved_by else '') +
                            u' дал согласие на добавление <b>' +
                            unicode(self.requested_time) + u' руб.</b> в <b>' +
                            unicode(templateTools.dateTime.convertToSite(self.requested_time_approve_date)) +
                            u'</b></div>'
                    )
                })

        addParams.update({
            'id': self.id,
            'userTo': {
                'id': self.userTo.id,
                'name': self.userTo.last_name + ' ' + self.userTo.first_name
            } if self.userTo else {},
            'task': {
                'id': self.task.id,
                'name': self.task.name,
                'url': self.task.url,
                'parent': {
                    'id': self.task.parentTask.id,
                    'name': self.task.parentTask.name,
                    'url': self.task.parentTask.url,
                } if self.task.parentTask else None
            } if self.task else {},
            'code': self.code,
            'text': self.text,
            'type': self.type,
            'read': self.read,
            'date': templateTools.dateTime.convertToSite(timezone.localtime(self.dateCreate)),
            'files': taskExtensions.getFileList(self.files.all()),
            # 'hidden_from_clients': self.hidden_from_clients,
            # 'hidden_from_responsible': self.hidden_from_responsible,
            'hidden': self.hidden,
            'system': self.isSystemLog,
            'todo': self.todo,
            'checked': self.checked,
            'bug': self.bug,
            'project': {
                'id': self.project.id,
                'name': self.project.name,
                'url': '/?project=' + str(self.project.id)
            } if self.project else None,
            'author': {
                'id': self.author.id,
                'name': self.author.first_name,
                'last_name': self.author.last_name,
                'username': self.author.username,
                'avatar': profileAuthor.avatarSrc,
                'avatar_color': profileAuthor.avatar_color
            } if self.author else {},
            'modifiedBy': {
                'last_name': self.modifiedBy.last_name,
                'first_name': self.modifiedBy.first_name
            } if self.modifiedBy else {},
            'dateModify': templateTools.dateTime.convertToSite(
                timezone.localtime(self.dateModify)) if self.dateModify else ''
        })

        if self.author and profileAuthor.avatarSrc:
            addParams.update({
                'avatar': thumbnail(profileAuthor.avatarSrc, '75x75', 3)
            })
        if self.code == 'GIT_COMMIT':
            addParams.update({
                'commit': self.commit,
                "canEdit": False,
                "canDelete": False
            })
            if cur_user:
                addParams.update({
                    "canView": self.canView(cur_user),
                })
        return addParams

    def canEdit(self, user):
        return (
                (self.author and self.author.id == user.id)
                or
                (self.project and user.get_profile().isManager(self.project))
        )

    def canDelete(self, user):
        return self.author and self.author.id == user.id

    def canView(self, user):
        if not user:
            return False

        if self.author and self.author.id == user.id:
            return True

        if self.userTo and self.userTo.id == user.id:
            return True

        prof = user.get_profile()
        if user.is_superuser and prof.hasRole(self.task.project):
            return True

        if self.hidden:
            return False

        if prof.isManager(self.task.project):
            return True

        if self.task.resp and self.task.resp.id == user.id:
            return True

        if self.task.parentTask and self.task.parentTask.resp and self.task.parentTask.resp.id == user.id:
            return True

        if prof.isEmployee(self.task.project) and \
                user.id in [u.id for u in self.task.observers.all()]:
            return True

        return (
                self.task.onPlanning and prof.hasRole(self.project, not_guest=True)
        )
        # todo: добавить про hidden_from_clients и from_employee

    def getUsersForNotice(self):
        pass

    class Meta:
        app_label = 'PManager'


class PM_Role(models.Model):
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=500)
    tracker = models.ForeignKey(PM_Tracker)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'PManager'


class PM_ProjectRoles(models.Model):
    type_choices = (
        ('real_time', u'За реальное время'),
        ('plan_time', u'За плановое время'),
        ('fix', u'Фиксированнаяза проект'),
    )
    user = models.ForeignKey(User, related_name='userRoles')
    project = models.ForeignKey(PM_Project, related_name='projectRoles')
    role = models.ForeignKey(PM_Role)
    rate = models.IntegerField(null=True, blank=True)
    payment_type = models.CharField(max_length=100, default='real_time', choices=type_choices)

    def __unicode__(self):
        return self.role.name + ' ' + self.project.name

    def isLastRequiredRole(self):
        lastRequiredRoleCode = 'manager'
        return self.role.code == lastRequiredRoleCode and \
               not PM_ProjectRoles.objects.filter(
                   project=self.project,
                   role__code=lastRequiredRoleCode
               ).exclude(id=self.id).exists()

    def safeDelete(self):
        if self.isLastRequiredRole():
            return False

        self.delete()
        return True

    class Meta:
        app_label = 'PManager'


class listManager:
    taskId = None
    modelClass = models

    def __init__(self, modelClass):
        self.modelClass = modelClass

    def validate(self, val, validator):
        if callable(validator):
            return validator(val)

    def validateInt(self, val):
        print 'int'
        val = int(val)
        return val

    def validateStr(self, val):
        print 'str'
        return val

    def validateFloat(self, val):
        print 'float'
        return val

    def validateDate(self, val):
        print 'date'
        return val

    def validateModel(self, val):
        print 'model'
        return val

    def validateUser(self, val):
        print 'user'
        return val

    def parseFilter(self, filter):
        if filter and isinstance(filter, dict):
            tempFilter = copy.deepcopy(filter)

            for field, val in tempFilter.iteritems():
                fitField = field[:]
                if '__' in fitField:
                    fitField = fitField[:fitField.index('__')]

                obj = self.modelClass({fitField: val})
                for i in obj._meta.fields:
                    field_name = i.get_attname()
                    if field_name == fitField or field_name == (fitField + '_id'):
                        try:
                            if field_name == (fitField + '_id'):
                                i.clean(val.id, self.modelClass())
                            else:
                                i.clean(val, self.modelClass())
                        except Exception:
                            del filter[field]  # validation error
        return filter


class PM_User_PlanTime(models.Model):
    user = models.ForeignKey(User)
    task = models.ForeignKey(PM_Task)
    time = models.FloatField(blank=True, null=True)

    def __unicode__(self):
        return self.user.username + ' ' + self.task.name

    def hour_rate(self):
        profile = self.user.get_profile()
        return profile.sp_price + profile.getRating(self.task.project)

    def total_cost(self):
        return self.time * self.hour_rate()

    class Meta:
        app_label = 'PManager'


class PM_Reminder(models.Model):
    task = models.ForeignKey(PM_Task)
    date = models.DateTimeField(blank=True, null=True, db_index=True, verbose_name='Напоминание')
    user = models.ForeignKey(User)

    def __unicode__(self):
        return unicode(self.date.strftime('%d.%m.%Y %H:%M:%S'))

    class Meta:
        app_label = 'PManager'


class PM_Holidays(models.Model):
    date = models.DateField('Нерабочий день')

    class Meta:
        app_label = 'PManager'

    def __unicode__(self):
        return self.date.strftime('%d-%m-%Y')


class RatingHistory(models.Model):
    value = models.FloatField(blank=True, verbose_name='Рейтинг', default=0)
    user = models.ForeignKey(User, blank=True, verbose_name='Пользователь', db_index=True)
    dateCreate = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        app_label = 'PManager'


class FineHistory(models.Model):
    value = models.FloatField(blank=True, verbose_name='Штраф', default=0)
    user = models.ForeignKey(User, blank=True, verbose_name='Пользователь', db_index=True)
    dateCreate = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return str(self.value) + ' ' + str(self.user)

    class Meta:
        app_label = 'PManager'


# SIGNALS

def setActivityOfMessageAuthor(sender, instance, created, **kwargs):
    if instance.author:
        prof = instance.author.get_profile()
        prof.last_activity_date = datetime.datetime.now()
        prof.save()


def setOnlySolution(sender, instance, **kwargs):
    if instance.solution:
        instance.code = u"SOLUTION"
        try:
            solution_messages_old = PM_Task_Message.objects.filter(code=u"SOLUTION", project=instance.task.project)
            for message in solution_messages_old:
                message.solution = False
                message.code = None
                message.save()
        except (PM_Task_Message.DoesNotExist, ValueError) as e:
            pass


def check_task_save(sender, instance, **kwargs):
    # При каждом сохранении задачи проверка, укладывается ли ответственный в свои задачи. Если нет, вывести сообщение.
    from PManager.services.check_milestone import check_milestones
    task = instance
    if not task.resp or task.closed:
        return

    try:
        origin = PM_Task.objects.get(id=task.id)

        if (
                task.critically == origin.critically and
                task.planTime == origin.planTime and
                (task.milestone.id if task.milestone else None) == (
                origin.milestone.id if origin.milestone else None) and
                (task.resp.id if task.resp else None) == (origin.resp.id if origin.resp else None)
        ):
            return
    except PM_Task.DoesNotExist:
        origin = {}

    overdueMilestones = check_milestones(task)
    if not overdueMilestones:
        return
    else:
        # task.critically = 0
        # Send message
        template = u'При изменении данного пункта '
        if task.lastModifiedBy == task.resp:
            template += u'высока вероятность ошибок по  '
        else:
            template += task.resp.last_name + u' ' + task.resp.first_name + u' высока вероятность ошибок по  '

        if len(overdueMilestones) > 1:
            template += u'следующим расчетам:'
            for milestone in overdueMilestones:
                template += "\n" + milestone['project__name'] + u': ' + milestone['name'] + ' '

        else:
            template += u'расчету ' + overdueMilestones[0]['project__name'] + u': ' + overdueMilestones[0]['name']

        template += "\n" + u'Измените критичность или ответственного по данному пункту, или сдвиньте сроки расчета.'

        secondsAgo = datetime.datetime.now() - datetime.timedelta(seconds=5)
        secondsAgo = timezone.make_aware(secondsAgo, timezone.get_default_timezone())

        lastMessages = PM_Task_Message.objects.filter(
            userTo=task.lastModifiedBy, author=task.resp,
            code='WARNING', text=template, dateCreate__gt=secondsAgo
        ).exists()  # Проверка на дублирование

        if not lastMessages:
            message = PM_Task_Message(text=template, task=task, project=task.project, author=task.resp,
                                      userTo=task.lastModifiedBy, code='WARNING', hidden=True)
            message.save()
            responseJson = message.getJson()

            mess = RedisMessage(service_queue,
                                objectName='comment',
                                type='add',
                                fields=responseJson
                                )
            mess.send()


post_save.connect(setActivityOfMessageAuthor, sender=PM_Task_Message)
pre_save.connect(setOnlySolution, sender=PM_Task_Message)
pre_save.connect(check_task_save, sender=PM_Task)