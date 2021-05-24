# -*- coding:utf-8 -*-
from django.db import DatabaseError

__author__ = 'Rayleigh'
from PManager.models.tasks import PM_Tracker


def get_tracker(prim_key=1):
    try:
        tracker = PM_Tracker.objects.get(pk=prim_key)
    except:
        return None
    else:
        return tracker
