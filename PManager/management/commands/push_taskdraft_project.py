# -*- coding: utf-8 -*-
__author__ = 'Rayleigh'
from tracker import settings
from django.core.management.base import BaseCommand
from optparse import Option
from PManager.models.taskdraft import TaskDraft
import os
ROOT = os.path.normpath(os.path.dirname(__file__))
make_option = Option


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--dry_run', action='store_true', dest='dry_run', help='Only check'),
    )

    def handle(self, *args, **options):
        try:
            self.process_drafts(options['dry_run'])
        except AssertionError:
            return 'ERROR: arguments failed to parse'

    def process_drafts(self, is_dry=False):
        drafts = TaskDraft.objects.filter(project_id=-1)
        for draft in drafts:
            tasks = draft.tasks.all()
            if tasks.count() == 0:
                continue
            task = tasks[:1].get()
            if is_dry:
                print("Task draft " + str(draft) + ": project - " + str(task.project))
            else:
                draft.project = task.project
                draft.save()




