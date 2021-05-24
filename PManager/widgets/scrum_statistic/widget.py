# -*- coding:utf-8 -*-
__author__ = 'Gvammer'
from PManager.viewsExt.tools import templateTools
from PManager.models import Credit, PM_Timer, PM_Milestone

import datetime

def dateToDb(date, type):
            if type is 'max' or type is 'min':
                date = datetime.datetime.combine(date, getattr(datetime.time, type))

            return templateTools.dateTime.convertToDb(date)


def widget(request, headerValues, a, b):
    milestone = PM_Milestone.objects.get(pk=request.GET.get('mid', 0))

    return {}