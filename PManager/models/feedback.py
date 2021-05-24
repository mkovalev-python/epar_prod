# -*- coding:utf-8 -*-
__author__ = 'Gvammer'

from django.contrib.auth.models import User
from django.db import models
from PManager.models import PM_Project


class Feedback(models.Model):
    user = models.ForeignKey(User)
    project = models.ForeignKey(PM_Project)
    meeting_time = models.CharField(max_length=32, null=True)
    demo_value = models.CharField(max_length=32, null=True)
    standup = models.CharField(max_length=32, null=True)
    speed = models.CharField(max_length=32, null=True)
    quality = models.CharField(max_length=32, null=True)
    notes_communications = models.CharField(max_length=500, null=True)
    notes_quality = models.CharField(max_length=500, null=True)
    rating = models.CharField(max_length=32, null=True)
    notes_was = models.CharField(max_length=500, null=True)
    notes_do = models.CharField(max_length=500, null=True)

    class Meta:
        app_label = 'PManager'