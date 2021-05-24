__author__ = 'rayleigh'
from django.contrib.auth.models import User
from PManager.services.activity import *
from django.test import TestCase
from PManager.models import PM_Project, PM_Task
from model_mommy import mommy
from django.utils import timezone
from datetime import timedelta


class ActivityTest(TestCase):
    def setUp(self):
        self.usr = mommy.make(User)
        self.project = mommy.make(PM_Project)

    def test_can_get_latest_project_activity(self):
        time = timezone.now()
        task = mommy.make(PM_Task, project=self.project, dateCreate=time)
        # todo first of all - PM_Task_Message throw warnings about naive datetime
        last_message = mommy.make(PM_Task_Message, task=task, author=self.usr, dateCreate=time)
        date = last_project_activity(self.project)
        # todo assert equal shows no clue how to compare date times, they differ in milliseconds
        self.assertIsNotNone(date)
        self.assertEqual(date.second, last_message.dateCreate.second)
        self.assertEqual(date.minute, last_message.dateCreate.minute)
        self.assertEqual(date.hour, last_message.dateCreate.hour)

    def test_can_get_activity_if_no_messages(self):
        task = mommy.make(PM_Task, project=self.project)
        date = last_project_activity(self.project)
        self.assertIsNotNone(date)
        self.assertEqual(date.second, task.dateModify.second)
        self.assertEqual(date.minute, task.dateModify.minute)
        self.assertEqual(date.hour, task.dateModify.hour)

    def test_can_get_activity_if_no_tasks(self):
        date = last_project_activity(self.project)
        self.assertIsNotNone(date)
        self.assertEqual(date.second, self.project.dateCreate.second)
        self.assertEqual(date.minute, self.project.dateCreate.minute)
        self.assertEqual(date.hour, self.project.dateCreate.hour)