# -*- coding:utf-8 -*-
from __future__ import division
__author__ = 'Gvammer'
from django.contrib.auth.models import User
from django.db import connection
from django.db import models

from PManager.models import PM_Project, PM_Task, PM_Milestone


class Credit(models.Model):
    '''
        Attribute:
            type: equals 0 if credit is plan, 1 if credit is fact
    '''
    CREDIT_CODE = (
        ('0', u'Не установлен'),
        ('1', u'Основная выплата'),
        ('2', u'Вычет программиста'),
        ('3', u'Бонус менеджера'),
    )
    user = models.ForeignKey(User, related_name='arrears', null=True, blank=True)
    payer = models.ForeignKey(User, related_name='credits', null=True, blank=True)
    project = models.ForeignKey(PM_Project, related_name='credits', null=True, blank=True)
    milestone = models.ForeignKey(PM_Milestone, related_name='credits', null=True, blank=True)
    task = models.ForeignKey(PM_Task, related_name='costs', null=True, blank=True)
    value = models.IntegerField()
    type = models.CharField(max_length=100, blank=True, null=True)
    code = models.CharField(max_length=32, choices=CREDIT_CODE, default='0')
    comment = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        app_label = 'PManager'

    @staticmethod
    def getUsersDebt(projects=None):
        if projects:
            projects = ' WHERE project_id IN (' + ','.join([str(s.id) for s in projects]) + ')'
        else:
            projects = ''

        qText = """
                  SELECT
                      sum(value) as summ, user_id FROM PManager_credit """ + projects + """ GROUP BY user_id
              """
        cursor = connection.cursor()

        cursor.execute(qText)

        arElems = []
        for x in cursor.fetchall():
            if not x[1]:
                continue

            arElems.append({
                'sum': x[0],
                'user_id': x[1]
            })

        return arElems

    def add_credit_developer(self, user, milestone, task):
        credit_type = 0
        fine = 0
        value = task.planTime * user.profile.sp_price
        if milestone.closed:
            credit_type = 1
            fine = value * 0.02 * milestone.final_delay

        Credit.objects.create(user=user, milestone=milestone, task=task, type=credit_type, value=value, code='1')

        if fine:
            Credit.objects.create(user=user, milestone=milestone, task=task, type=credit_type, value=-fine, code='2')

    def add_credit_manager(self, user, milestone):
        credit_type = 0
        base_hours = 56
        base_part = 13000
        bonus_part = 6000

        hours = int(milestone.type) + milestone.extra_hours

        value = hours / base_hours * base_part
        bonus = hours / base_hours * bonus_part

        if milestone.closed:
            credit_type = 1
            g = milestone.g_factor
            k = int(milestone.is_half_completed)
            m = int(milestone.is_has_grooming)
            l = milestone.delay_factor
            bonus = (bonus / 2 * g + bonus / 4 * k + bonus / 4 * m) * l

        if value:
            Credit.objects.create(user=user, milestone=milestone, type=credit_type, value=value, code='1')
        if bonus:
            Credit.objects.create(user=user, milestone=milestone, type=credit_type, value=bonus, code='3')


class PaymentRequest(models.Model):
    user = models.ForeignKey(User, related_name='payment_requests', null=True, blank=True)
    project = models.ForeignKey(PM_Project, related_name='payment_requests', null=True, blank=True)
    value = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        app_label = 'PManager'


class Fee(models.Model):
    user = models.ForeignKey(User, related_name='fee', null=True, blank=True)
    project = models.ForeignKey(PM_Project, related_name='fee', null=True, blank=True)
    value = models.IntegerField()
    task = models.ForeignKey(PM_Task, related_name='fee', null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    type = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        app_label = 'PManager'
