# -*- coding:utf-8 -*-
import datetime
import hashlib

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.dateparse import parse_datetime
from django.utils.timezone import now
from mock import patch, PropertyMock
from model_mommy import mommy

from PManager.models import PM_Milestone, PM_MilestoneStatus, User, PM_Task


class PMMilestoneTestCase(TestCase):
    def setUp(self):
        self.user = mommy.make(User)

    @patch('PManager.models.tasks.PM_Milestone.set_status')
    @patch('PManager.models.tasks.Telegram.send')
    def _close_milestone(self, milestone, status, closed_status, call_count, _, mock_set_status):
        mommy.make(PM_MilestoneStatus, sprint=milestone, status=PM_MilestoneStatus.STATUS_STARTED)
        mommy.make(PM_MilestoneStatus, sprint=milestone, status=status)
        result = milestone.close_milestone(now(), self.user)
        print result['message']
        self.assertEqual(result['is_closed'], closed_status)
        milestone = PM_Milestone.objects.get(pk=milestone.pk)
        self.assertEqual(milestone.closed, closed_status)
        self.assertEqual(mock_set_status.called, call_count)

    def test_create_md5(self):
        milestone = mommy.make(PM_Milestone)
        milestone.save()
        milestone = PM_Milestone.objects.get(pk=milestone.pk)
        self.assertEqual(milestone.id_md5, hashlib.md5('{}:salt'.format(milestone.id)).hexdigest())

    def test_get_support_url(self):
        milestone = mommy.make(PM_Milestone)
        milestone.save()
        milestone = PM_Milestone.objects.get(pk=milestone.pk)
        url = reverse('support_page:milestone-form', kwargs={'hash': milestone.id_md5})
        self.assertEqual(milestone.support_url, url)

    def test_cannot_close_milestone(self):
        milestone = mommy.make(PM_Milestone, manager=self.user)
        self._close_milestone(milestone, PM_MilestoneStatus.STATUS_DRAFT, False, 0)
        self._close_milestone(milestone, PM_MilestoneStatus.STATUS_PAUSED_AFTER_RATED, False, 0)
        self._close_milestone(milestone, PM_MilestoneStatus.STATUS_PAUSED_AFTER_STARTED, False, 0)
        self._close_milestone(milestone, PM_MilestoneStatus.STATUS_STARTED, False, 0)
        self._close_milestone(milestone, PM_MilestoneStatus.STATUS_RESUMED, False, 0)
        self._close_milestone(milestone, PM_MilestoneStatus.STATUS_PAUSED, False, 0)
        mommy.make(PM_Task, milestone=milestone, active=True, closed=False)
        self._close_milestone(milestone, PM_MilestoneStatus.STATUS_RATED, False, 0)

    @patch('PManager.models.payments.Credit.add_credit_manager')
    def test_can_close_milestone(self, _):
        milestone = mommy.make(PM_Milestone, manager=self.user, date=now())

        mommy.make(PM_Task, milestone=milestone, active=True, closed=True,
                   dateClose=parse_datetime('2020-05-31T00:11:12+0300'))

        start_status = mommy.make(PM_MilestoneStatus, sprint=milestone, status=PM_MilestoneStatus.STATUS_STARTED,
                                  start_date=parse_datetime('2020-05-21T00:11:12+0300'))
        start_status.date_create = parse_datetime('2020-05-21T00:11:12+0300')
        start_status.save()

        next_status = mommy.make(PM_MilestoneStatus, sprint=milestone, status=PM_MilestoneStatus.STATUS_RATED)
        next_status.date_create = parse_datetime('2020-05-31T00:11:12+0300')
        next_status.save()

        result = milestone.close_milestone(now(), self.user)
        self.assertTrue(result['is_closed'])
        milestone = PM_Milestone.objects.get(pk=milestone.pk)
        self.assertTrue(milestone.closed)

    def _create_tasks(self, **kwargs):
        create_date = kwargs.pop('create_date')
        tasks = mommy.make(PM_Task, **kwargs)
        for task in tasks:
            task.dateCreate = parse_datetime(create_date)
            task.save()

    @patch('PManager.models.PM_Milestone.start_date', new_callable=PropertyMock)
    def test_has_grooming(self, mock_start_date):
        mock_start_date.return_value = parse_datetime('2020-05-01T00:00:01+0300').date()
        milestone1 = mommy.make(PM_Milestone, date=parse_datetime('2020-05-31T00:00:02+0300'))
        milestone2 = mommy.make(PM_Milestone)
        self._create_tasks(**{
            'milestone': milestone2,
            'active': True,
            'closed': False,
            '_quantity': 2,
            'create_date': '2020-05-11T00:00:02+0300'
        })
        self.assertTrue(milestone1._is_has_grooming())

    @patch('PManager.models.PM_Milestone.start_date', new_callable=PropertyMock)
    def test_no_grooming(self, mock_start_date):
        mock_start_date.return_value = parse_datetime('2020-05-01T00:00:01+0300').date()
        milestone = mommy.make(PM_Milestone, date=parse_datetime('2020-05-31T00:00:02+0300'))
        # current milestone
        self._create_tasks(**{
            'milestone': milestone,
            'active': True,
            'closed': False,
            '_quantity': 2,
            'create_date': '2020-05-11T00:00:02+0300'
        })
        # task not active
        self._create_tasks(**{
            'active': False,
            'closed': False,
            '_quantity': 2,
            'create_date': '2020-05-11T00:00:02+0300'
        })
        # task closed
        self._create_tasks(**{
            'active': True,
            'closed': True,
            '_quantity': 2,
            'create_date': '2020-05-11T00:00:02+0300'
        })
        # create date lower then sprint start date
        self._create_tasks(**{
            'active': True,
            'closed': False,
            '_quantity': 2,
            'create_date': '2020-04-11T00:00:02+0300'
        })
        # create date greater then sprint start date
        self._create_tasks(**{
            'active': True,
            'closed': False,
            '_quantity': 2,
            'create_date': '2020-06-11T00:00:02+0300'
        })
        self.assertFalse(milestone._is_has_grooming())

    @patch('PManager.models.PM_Milestone.start_date', new_callable=PropertyMock)
    def test_is_half_completed(self, mock_start_date):
        mock_start_date.return_value = now().date() + datetime.timedelta(days=1)
        milestone = mommy.make(PM_Milestone, closed=True, date=now())
        mommy.make(PM_Task, milestone=milestone, dateClose=now(), planTime=51)
        mommy.make(PM_Task, milestone=milestone, dateClose=now() + datetime.timedelta(days=6), planTime=49)
        self.assertTrue(milestone._is_half_completed())

    @patch('PManager.models.PM_Milestone.start_date', new_callable=PropertyMock)
    def test_not_half_completed(self, mock_start_date):
        mock_start_date.return_value = now().date() + datetime.timedelta(days=1)
        milestone = mommy.make(PM_Milestone, closed=True, date=now())
        mommy.make(PM_Task, milestone=milestone, dateClose=now(), planTime=49)
        mommy.make(PM_Task, milestone=milestone, dateClose=now() + datetime.timedelta(days=9), planTime=51)
        self.assertFalse(milestone._is_half_completed())

    def test_delay_factor_1(self):
        milestone = mommy.make(PM_Milestone, final_delay=0)
        self.assertEqual(milestone._get_delay_factor(), 1)

    def test_delay_factor_07(self):
        milestone = mommy.make(PM_Milestone, final_delay=1)
        self.assertEqual(milestone._get_delay_factor(), 0.7)
        milestone = mommy.make(PM_Milestone, final_delay=2)
        self.assertEqual(milestone._get_delay_factor(), 0.7)

    def test_delay_factor_05(self):
        milestone = mommy.make(PM_Milestone, final_delay=3)
        self.assertEqual(milestone._get_delay_factor(), 0.5)
        milestone = mommy.make(PM_Milestone, final_delay=4)
        self.assertEqual(milestone._get_delay_factor(), 0.5)
        milestone = mommy.make(PM_Milestone, final_delay=5)
        self.assertEqual(milestone._get_delay_factor(), 0.5)

    def test_delay_factor_0(self):
        milestone = mommy.make(PM_Milestone, final_delay=6)
        self.assertEqual(milestone._get_delay_factor(), 0)
        milestone = mommy.make(PM_Milestone, final_delay=7)
        self.assertEqual(milestone._get_delay_factor(), 0)
