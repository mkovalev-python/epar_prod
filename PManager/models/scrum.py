# -*- coding:utf-8 -*-
__author__ = 'Gvammer'
from PManager.models.tasks import PM_Milestone
from django.db import models

class PM_MilestoneChanges(models.Model):
    milestone = models.ForeignKey(PM_Milestone, related_name='changes')
    value = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'PManager'