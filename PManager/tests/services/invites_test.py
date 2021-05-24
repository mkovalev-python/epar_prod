__author__ = 'rayleigh'
from django.contrib.auth.models import User
from django.test import TestCase
from PManager.models import PM_Project, PM_Task, PM_Milestone, TaskDraft
from model_mommy import mommy
from model_mommy.recipe import related, Recipe
from datetime import datetime, timedelta
from django.utils import timezone
from PManager.services.invites import *


class TaskDraftsTestCase(TestCase):
    def setUp(self):
        self.project = mommy.make(PM_Project)
        self.usr = mommy.prepare(User)
        self.date_6_days_ago = timezone.now() - timedelta(days=6)
        self.date_4_days_ago = timezone.now() - timedelta(days=4)
        self.date_3_days_ago = timezone.now() - timedelta(days=3)
        self.now = timezone.now()
        self.tomorrow = timezone.now() + timedelta(days=1)

    def test_should_report_project_if_no_activity_in_5_days(self):
        project = mommy.prepare(PM_Project, dateCreate=self.date_6_days_ago)
        self.assertTrue(should_suggest_outsource(project))
        self.assertTrue(is_project_stale(project))

    def test_should_not_report_if_activity_within_5_days(self):
        project = mommy.prepare(PM_Project, dateCreate=self.date_4_days_ago)
        project2 = mommy.prepare(PM_Project, dateCreate=self.date_3_days_ago)
        self.assertFalse(should_suggest_outsource(project))
        self.assertFalse(should_suggest_outsource(project2))

    def test_should_report_project_if_deadline_reached_for_task(self):
        project = mommy.make(PM_Project)
        mommy.make(PM_Task, deadline=timezone.now(), closed=False, project=project)
        self.assertTrue(has_dead_tasks(project), "should have dead tasks, cause deadline is now")
        self.assertTrue(should_suggest_outsource(project), "should suggest outsource if has a dead task")

    def test_should_report_project_if_deadline_reached_for_milestone(self):
        project = mommy.make(PM_Project)
        mommy.make(PM_Milestone, overdue=True, closed=False, project=project)
        self.assertTrue(has_dead_milestones(project), "should have dead milestones")
        self.assertTrue(should_suggest_outsource(project), "should suggest outsource if has a dead milestone")

    def test_should_report_if_tasks_will_reach_deadline_by_plan_time(self):
        self.will_reach_deadline_test(30., True)
        self.will_reach_deadline_test(40., True)
        self.will_reach_deadline_test(60., True)

    def will_reach_deadline_test(self, planTime, result):
        deadline_planned_time = timezone.now() + timedelta(days=7)
        task_on_the_edge = mommy.make(PM_Task, closed=False,
                                      deadline=deadline_planned_time, project=self.project, planTime=planTime)
        self.assertEqual(should_suggest_outsource(self.project), result,
                         "planTime is inadequate, was %s" % planTime)

    def test_should_not_report_if_tasks_will_not_reach_deadline_by_plan_time(self):
        self.will_reach_deadline_test(20., False)

    def get_taskdraft(self):
        taskdraft = mommy.make(TaskDraft, make_m2m=True)
        return taskdraft

    def get_users(self):
        return dict()


