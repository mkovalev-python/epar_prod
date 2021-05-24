# -*- coding:utf-8 -*-
__author__ = 'tracker_maker'
from django.core.management.base import NoArgsCommand
from PManager.models import PM_Milestone


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        PM_Milestone.check()
