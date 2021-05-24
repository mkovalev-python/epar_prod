# -*- coding:utf-8 -*-
__author__ = 'Gvammer'
from PManager.models import PM_Achievement

def widget(request,headerValues,ar,qargs):
    achievements = PM_Achievement.objects.all()
    for ach in achievements:
        if ach.achievement_users.filter(user=request.user):
            setattr(ach, 'mine', True)

    return {'achievements': achievements, 'title': u'Достижения'}