from django.test import TestCase
from PManager.models import TaskDraft
from PManager.models.tasks import PM_Project, PM_Tracker, PM_Task
from django.contrib.auth.models import User
from model_mommy import mommy


class TaskDraftTestCase(TestCase):
    def setUp(self):
        self.tracker = mommy.make(PM_Tracker, id=1)
        self.usr = mommy.make(User, username="test")
        self.usr2 = mommy.make(User, username="test2")
        self.pro = mommy.make(PM_Project)
        self.task1 = mommy.make(PM_Task, project=self.pro, author=self.usr)
        self.task2 = mommy.make(PM_Task, project=self.pro, author=self.usr)

    def test_TaskDraft_test(self):
        tl = TaskDraft.objects.create(author=self.usr)
        self.assertIsNotNone(tl.pk, "TaskDraft should be saved properly")
        self.assertEqual(tl.status, TaskDraft.CLOSED, "TaskDraft should be created with default closed status")

    def test_TaskDraft_closed_at_should_be_null_at_start(self):
        tl = TaskDraft.objects.create(author=self.usr)
        self.assertIsNone(tl.closed_at, "Closed_at field should not be set immediately after creation")

    def test_TaskDraft_forced_close_if_empty_tasks_or_users(self):
        tl = TaskDraft.objects.create(status=TaskDraft.OPEN, author=self.usr)
        self.assertEqual(tl.status, TaskDraft.CLOSED, "Status should be closed after list creation")
        tl.status = TaskDraft.OPEN
        tl.save()
        tl2 = TaskDraft.objects.get(pk=tl.id)
        self.assertEqual(tl2.status, TaskDraft.CLOSED, "TaskDraft should be saved with forced data on pre_save signal")

    def test_should_not_add_closed_at_at_second_save(self):
        tl = TaskDraft.objects.create(author=self.usr)
        tl.save()
        self.assertIsNone(tl.closed_at, "Closed_at field should not be set on re-save")
        tl.status = TaskDraft.CLOSED
        tl.save()
        self.assertIsNone(tl.closed_at, "Closed_at field should not be set on re-save")

    def test_TaskDraft_would_open(self):
        tl = TaskDraft.objects.create(author=self.usr)
        tl.users.add(self.usr)
        tl.tasks.add(self.task1)
        tl.status = TaskDraft.OPEN
        tl.save()
        self.assertEqual(tl.status, TaskDraft.OPEN)

    def test_TaskDraft_closing_should_set_closed_at(self):
        tl = TaskDraft.objects.create(author=self.usr)
        self.assertIsNone(tl.closed_at)
        tl.users.add(self.usr)
        tl.tasks.add(self.task1)
        tl.status = TaskDraft.OPEN
        tl.save()
        self.assertIsNone(tl.closed_at)
        tl.status = TaskDraft.CLOSED
        tl.save()
        self.assertIsNotNone(tl.closed_at)

    def test_TaskDraft_add_users_and_tasks(self):
        # default status should be closed
        tl = TaskDraft.objects.create(author=self.usr)
        self.assertEqual(tl.status, TaskDraft.CLOSED)
        tl.tasks.add(self.task1)
        tl.users.add(self.usr)
        tl.status = TaskDraft.OPEN
        tl.save()
        # status with tasks and users should be open
        self.assertEqual(tl.status, TaskDraft.OPEN)
        tl2 = TaskDraft.objects.get(pk=tl.id)
        self.assertIsNotNone(tl2.users)
        self.assertIsNotNone(tl2.tasks)

