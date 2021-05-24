# -*- coding:utf-8 -*-
from django.conf.urls import url

from .views import MilestoneFormView, ProjectFormView

urlpatterns = (
    url(r'm/(?P<hash>[a-zA-Z0-9_-]+)', MilestoneFormView.as_view(), name='milestone-form'),
    url(r'p/(?P<hash>[a-zA-Z0-9_-]+)', ProjectFormView.as_view(), name='project-form'),
)
