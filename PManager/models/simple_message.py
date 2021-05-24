# -*- coding:utf-8 -*-
__author__ = 'Rayleigh'
from django.db import models
from django.contrib.auth.models import User
from PManager.models.tasks import PM_Task
from PManager.models.taskdraft import TaskDraft


class SimpleMessage(models.Model):
    author = models.ForeignKey(User, blank=False, related_name='simple_messages')
    text = models.TextField(blank=False, max_length=10000)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    task = models.ForeignKey(PM_Task, blank=False)
    task_draft = models.ForeignKey(TaskDraft, blank=False)

    def __unicode__(self):
        return "%s#%s" % (str(self.id), self.author.get_full_name())

    class Meta:
        app_label = 'PManager'

