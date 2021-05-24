# -*- coding:utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
__author__ = 'Gvammer'


class Agreement(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    payer = models.ForeignKey(User, related_name='payer_agreements', db_index=True)
    resp = models.ForeignKey(User, related_name='resp_agreements', db_index=True)
    jsonData = models.TextField()
    approvedByPayer = models.BooleanField(default=False, blank=True)
    datePayerApprove = models.DateTimeField(null=True, blank=True)
    approvedByResp = models.BooleanField(default=False, blank=True)
    dateRespApprove = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)

    def __unicode__(self):
        return unicode(self.id)

    @property
    def text(self):
        with open('PManager/static/agreement.html') as f:
            html = f.read()

        data = {
            'PAYER_NAME': self.payer.first_name,
            'PAYER_LAST_NAME': self.payer.last_name,
            'RESP_NAME': self.resp.first_name,
            'RESP_LAST_NAME': self.resp.last_name,
            'DATE': self.date.strftime('%d.%m.%Y'),
            'NUMBER': str(self.id)
        }

        #html = unicode(html).replace('1', '2')
        # for i, k in data.iteritems():
        #     html = html.replace(u'#' + unicode(i) + u'#', unicode(k))

        return html

    class Meta:
        app_label = 'PManager'