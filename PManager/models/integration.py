# -*- coding:utf-8 -*-
__author__ = 'Gvammer'
from django.db import models
from PManager.models.tasks import PM_Project
import json, urllib2, urllib

class Integration(models.Model):
    project = models.ForeignKey(PM_Project)
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    lastSendDate = models.DateTimeField(blank=True, null=True)

    class Meta:
        app_label = 'PManager'

class SlackIntegration(Integration):
    def send(self, params):
        if self.url:
            post_data = [('payload', json.dumps(params)), ]
            result = urllib2.urlopen(self.url, urllib.urlencode(post_data))
            content = result.read()
            return content == 'ok'

        return False

    class Meta:
        app_label = 'PManager'
