# -*- coding:utf-8 -*-
__author__ = 'Rayleigh'
from django.http import Http404
from PManager.services.task_drafts import drafts
from django.contrib.auth.models import User


def widget(request, header_values, ar, qargs):
    user = request.user
    if not user.is_authenticated():
        raise Http404
    draft_list = drafts(user).all()
    return {
        "drafts": draft_list,
        "headers": header_values,
        "title": u'Списки задач'
    }
