__author__ = 'Gvammer'
from django.db import models
from django.contrib.auth.models import User

class LogData(models.Model):
    code = models.CharField(db_index=True, max_length=255)
    datetime = models.DateTimeField(db_index=True, auto_now_add=True)
    user = models.ForeignKey(User, db_index=True, null=True, blank=True)
    value = models.IntegerField()
    project_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.code + ' ' + str(self.value)

    class Meta:
        app_label = 'PManager'