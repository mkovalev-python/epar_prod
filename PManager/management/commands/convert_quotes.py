# -*- coding: utf-8 -*-
__author__ = 'Tonakai'
from tracker import settings
from django.core.management.base import BaseCommand
from optparse import Option
from PManager.models.tasks import PM_Task_Message
import os
import re
ROOT = os.path.normpath(os.path.dirname(__file__))
make_option = Option


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--dry-run', action='store_true', dest='dry', help='Only output convert result'),
    )
    def handle(self, *args, **options):
        self.__convert_quotes(options['dry'])

    def __convert_quotes(self, dry_run):
         repl = re.compile(ur'&gt;&gt; (.+?)(\r\n|\n)', re.UNICODE)
         msgs = PM_Task_Message.objects.filter(code__isnull=True)
         for msg in msgs:
            print "-------MESSAGE--------" + str(msg.id) + "-------------------"
            # print msg.text
            print len(msg.text)
            msg.text = repl.sub(r'[Q]\1[/Q]', unicode(msg.text))

            if not dry_run:
                msg.save()
            print "----------END------------"

