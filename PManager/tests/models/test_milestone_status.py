import mock
from django.test import TestCase
from model_mommy import mommy

from PManager.models import PM_MilestoneStatus, User, PM_Milestone, PM_Project, PM_ProjectRoles


@mock.patch('PManager.models.tasks.EmailMessage')
@mock.patch('PManager.models.tasks.Telegram.send')
class PMMilestoneStatusModelTelegramMessageTestCase(TestCase):
    def setUp(self):
        self.manager = mommy.make(User)
        self.sprint = mommy.make(PM_Milestone, manager=self.manager, extra_hours=10)

    def test_status_draft_send_message(self, send_mock, _):
        mommy.make(PM_MilestoneStatus, sprint=self.sprint, status=PM_MilestoneStatus.STATUS_DRAFT)
        self.assertEqual(send_mock.call_count, 0)

    def test_status_started_send_message(self, send_mock, _):
        mommy.make(PM_MilestoneStatus, sprint=self.sprint, status=PM_MilestoneStatus.STATUS_STARTED)
        self.assertEqual(send_mock.call_count, 1)

    def test_status_rated_send_message_without_extra_hours(self, send_mock, _):
        # milestone without extra hours
        sprint = mommy.make(PM_Milestone, manager=self.manager)
        mommy.make(PM_MilestoneStatus, sprint=sprint, status=PM_MilestoneStatus.STATUS_RATED)
        self.assertEqual(send_mock.call_count, 1)

    def test_status_rated_send_message_with_extra_hours(self, send_mock, _):
        # milestone with extra hours
        mommy.make(PM_MilestoneStatus, sprint=self.sprint, status=PM_MilestoneStatus.STATUS_RATED)
        self.assertEqual(send_mock.call_count, 2)

    def test_status_paused_send_message(self, send_mock, _):
        mommy.make(PM_MilestoneStatus, sprint=self.sprint, status=PM_MilestoneStatus.STATUS_PAUSED)
        mommy.make(PM_MilestoneStatus, sprint=self.sprint, status=PM_MilestoneStatus.STATUS_PAUSED_AFTER_RATED)
        mommy.make(PM_MilestoneStatus, sprint=self.sprint, status=PM_MilestoneStatus.STATUS_PAUSED_AFTER_STARTED)
        self.assertEqual(send_mock.call_count, 3)

    def test_status_resumed_send_message(self, send_mock, _):
        mommy.make(PM_MilestoneStatus, sprint=self.sprint, status=PM_MilestoneStatus.STATUS_RESUMED)
        self.assertEqual(send_mock.call_count, 1)

    def test_status_closed_send_message(self, send_mock, _):
        mommy.make(PM_MilestoneStatus, sprint=self.sprint, status=PM_MilestoneStatus.STATUS_CLOSED)
        self.assertEqual(send_mock.call_count, 1)


@mock.patch('PManager.models.tasks.EmailMessage.send')
@mock.patch('PManager.models.tasks.Telegram')
class PMMilestoneStatusModelEmailMessageTestCase(TestCase):
    def setUp(self):
        manager = mommy.make(User, email='test@mail')
        user1 = mommy.make(User, email='test@mail')
        user2 = mommy.make(User, email='test@mail')

        project = mommy.make(PM_Project)
        mommy.make(PM_ProjectRoles, project=project, user=manager)
        mommy.make(PM_ProjectRoles, project=project, user=user1)
        mommy.make(PM_ProjectRoles, project=project, user=user2)
        self.sprint = mommy.make(PM_Milestone, project=project, manager=manager)

    def test_send_email(self, _, mock_email):
        mommy.make(PM_MilestoneStatus, sprint=self.sprint, status=PM_MilestoneStatus.STATUS_RATED)
        self.assertEqual(mock_email.call_count, 3)
