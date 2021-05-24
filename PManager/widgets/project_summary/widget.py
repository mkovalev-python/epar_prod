# -*- coding:utf-8 -*-
__author__ = 'Gvammer'
from PManager.models import PM_Timer, PM_Task, Credit, Fee, PM_Project
import datetime
from django.db.models import Sum

def widget(request, headerValues, a, b):
    if request.user.is_superuser:
        if request.user.is_superuser:
            projects = PM_Project.objects.all()
        else:
            projects = request.user.get_profile().getProjects(only_managed=True)

        feeAll = Fee.objects.raw('SELECT SUM(value) s, id from pmanager_fee where value > 0')
        feeAll = feeAll[0].s

        aProjects = []

        for project in projects:
            projectSum = 0

            credit = Credit.objects.filter(
                    project=project,
                    value__lt=0,
                    type="Client with comission"
                ).aggregate(Sum('value'))
            projectSum = -(credit['value__sum'] or 0)

            credit = Credit.objects.filter(
                    project=project,
                    value__gt=0,
                ).exclude(type="Client with comission").aggregate(Sum('value'))
            projectSumPayed = credit['value__sum'] or 0

            if not projectSumPayed:
                continue

            credit = Fee.objects.filter(
                    project=project,
                    value__gt=0,
                ).aggregate(Sum('value'))
            feeSum = credit['value__sum'] or 0

            setattr(project, 'projectSum', projectSum)
            setattr(project, 'projectSumPayed', projectSumPayed)
            setattr(project, 'feeSum', feeSum)

            aProjects.append(project)

        return {
            'projects': aProjects,
            'title': u'Сводка по проектам',
            'feeAll': feeAll,
            'comission': PM_Task.FEE
        }