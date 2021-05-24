__author__ = 'Gvammer'
from django.db import models
from django.contrib.auth.models import User
import datetime
from django.utils import timezone
from django.db.models import Q
from PManager.customs.storages import path_and_rename

class PM_Notice(models.Model):
    name = models.CharField(max_length=100)
    html = models.CharField(max_length=1000)
    image = models.ImageField(upload_to=path_and_rename("notices"), null=True, blank=True)
    url = models.CharField(max_length=200, blank=True, null=True)
    itemClass = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

    @property
    def src(self):
        return '/media/' + str(self.image)\
            .replace('PManager/static/upload', '') #todo: remove after reupload notice images

    @staticmethod
    def getForUser(user, path):
        if not path: path = '/'
        if user and user.is_authenticated():
            dateLast = timezone.make_aware(datetime.datetime.now() - datetime.timedelta(minutes=1),
                                           timezone.get_default_timezone())
            lastNotice = PM_NoticedUsers.objects.filter(user=user, date__gt=dateLast)
            if not lastNotice:
                notices = PM_Notice.objects.exclude(
                    pk__in=PM_NoticedUsers.objects.filter(user=user).values('notice__id')) \
                    .filter(Q(url=path) | Q(url__isnull=True)).order_by('?')

                if notices:
                    return notices[0]
        return None

    def setRead(self, user):
        return PM_NoticedUsers.objects.create(user=user, notice=self)

    class Meta:
        app_label = 'PManager'


class PM_NoticedUsers(models.Model):
    user = models.ForeignKey(User, related_name='notices')
    notice = models.ForeignKey(PM_Notice, related_name='userNotices')
    date = models.DateTimeField(default=datetime.datetime.now().replace(microsecond=0))

    def __unicode__(self):
        return self.notice.name + " - " + self.user.username

    class Meta:
        app_label = 'PManager'
