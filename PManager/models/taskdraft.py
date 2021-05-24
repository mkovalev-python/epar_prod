# -*- coding:utf-8 -*-
__author__ = 'Tonakai'
from django.db import models
from PManager.models.tasks import PM_Project, PM_Task
from PManager.models.users import Specialty
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.utils import timezone


class TaskDraft(models.Model):
    OPEN = 1
    CLOSED = 0
    status_choices = (
        (OPEN, u'Открыт'),
        (CLOSED, u'Закрыт')
    )
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    title = models.CharField(max_length=250, unique=False, blank=True)
    slug = models.CharField(max_length=64, unique=True, blank=False)
    users = models.ManyToManyField(User, blank=True)
    author = models.ForeignKey(User, blank=False, related_name='task_drafts')
    project = models.ForeignKey(PM_Project, blank=False, null=True, related_name='task_drafts')
    tasks = models.ManyToManyField(PM_Task, blank=True)
    closed_at = models.DateTimeField(blank=True, null=True)
    deleted = models.BooleanField(blank=False, default=False)
    specialties = models.ManyToManyField(Specialty, blank=True)
    _status = models.IntegerField(blank=True, null=True, default=CLOSED, choices=status_choices, db_column='status')

    def __unicode__(self):
        if self.title:
            return self.project.name + ': ' + self.title
        return self.project.name

    def status_humanize(self):
        for choice in self.status_choices:
            if choice[0] == self._status:
                return choice[1]
        return self.status_choices[1][1]  # return CLOSED by default

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, new_status):
        sanitized_status = self._sanitaze_status(new_status)
        if sanitized_status == TaskDraft.CLOSED and sanitized_status != self.status:
            self.closed_at = timezone.now()
        self._status = sanitized_status

    def _sanitaze_status(self, new_status):
        if self.pk is None:
            return TaskDraft.CLOSED
        if new_status == TaskDraft.OPEN:
            if self.tasks.count() == 0 or self.users.count() == 0:
                return TaskDraft.CLOSED
        return new_status

    class Meta:
        app_label = 'PManager'
