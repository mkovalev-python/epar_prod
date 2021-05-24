# -*- coding:utf-8 -*-
__author__ = 'Rayleigh'

from django.template import Library

from tracker import settings

register = Library()


@register.simple_tag(name='get_settings')
def get_settings(setting_name):
    if hasattr(settings, setting_name):
        return getattr(settings, setting_name)
    return ""
