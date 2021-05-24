from datetime import timedelta, datetime

from django.test import TestCase
from django.utils.dateparse import parse_datetime
from django.utils.timezone import now
from model_mommy import mommy

from PManager.models import PM_Milestone, PM_Holidays, templateTools


class MilestoneTestCase(TestCase):
    def test_get_plan_end_date_naive(self):
        date = templateTools.dateTime.convertToDateTime('21.05.2020')
        test_date = parse_datetime('2020-05-21T00:11:12+0300')
        milestone = mommy.make(PM_Milestone, date=date)
        self.assertEqual(milestone.get_plan_end_date(), test_date.date())

    def test_get_plan_end_date_tz(self):
        date = parse_datetime('2020-05-21T10:11:12+0300')
        milestone = mommy.make(PM_Milestone, date=date)
        self.assertEqual(milestone.get_plan_end_date(), date.date())

    def test_end_date_none(self):
        milestone = mommy.make(PM_Milestone, date=None)
        self.assertEqual(milestone.get_real_end_date(), None)

    def test_end_date_not_closed(self):
        today = now()
        yesterday = parse_datetime('2020-05-20T10:11:12+0300')
        milestone = mommy.make(PM_Milestone, date=yesterday)
        self.assertEqual(milestone.get_real_end_date(), today.date())

    def test_end_date_closed(self):
        today = parse_datetime('2020-05-21T10:11:12+0300')
        yesterday = parse_datetime('2020-05-20T10:11:12+0300')
        milestone = mommy.make(PM_Milestone, date=yesterday, fact_close_date=today)
        self.assertEqual(milestone.get_real_end_date(), today.date())

    def test_end_date_closed_naive(self):
        today = templateTools.dateTime.convertToDateTime('21.05.2020')
        yesterday = templateTools.dateTime.convertToDateTime('20.05.2020')
        milestone = mommy.make(PM_Milestone, date=yesterday, fact_close_date=today)
        self.assertEqual(milestone.get_real_end_date(), today.date())

    def test_delay_days_no_delay(self):
        today = parse_datetime('2020-05-21T10:11:12+0300')
        yesterday = parse_datetime('2020-05-20T10:11:12+0300')
        milestone = mommy.make(PM_Milestone, date=today, fact_close_date=yesterday)
        self.assertEqual(milestone.delay_days, 0)

    def test_delay_days_w_delay(self):
        """
        2020-05-21 - thursday
        2020-05-22 - friday
        2020-05-23 - saturday
        2020-05-24 - sunday
        2020-05-25 - monday
        """
        date_now = parse_datetime('2020-05-21T10:11:12+0300')
        milestone = mommy.make(PM_Milestone, date=date_now)
        milestone.fact_close_date=date_now + timedelta(days=1)
        milestone.save()
        self.assertEqual(milestone.delay_days, 1)
        milestone.fact_close_date=date_now + timedelta(days=2)
        milestone.save()
        self.assertEqual(milestone.delay_days, 1)
        milestone.fact_close_date=date_now + timedelta(days=3)
        milestone.save()
        self.assertEqual(milestone.delay_days, 1)
        milestone.fact_close_date=date_now + timedelta(days=4)
        milestone.save()
        self.assertEqual(milestone.delay_days, 2)

    def test_delay_days_w_holidays_2(self):
        """
        2020-05-21 - thursday
        2020-05-22 - friday
        2020-05-23 - saturday
        2020-05-24 - sunday
        2020-05-25 - monday
        """
        mommy.make(PM_Holidays, date=datetime.strptime('2020-05-22', '%Y-%m-%d').date())
        date_now = parse_datetime('2020-05-21T10:11:12+0300')
        milestone = mommy.make(PM_Milestone, date=date_now)
        milestone.fact_close_date=date_now + timedelta(days=4)
        milestone.save()
        self.assertEqual(milestone.delay_days, 1)
