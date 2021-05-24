import datetime

from django.test import TestCase
from django.utils.timezone import now
from mock import patch, PropertyMock
from model_mommy import mommy

from PManager.models import User, PM_Milestone, PM_Task, Credit


class CreditTestCase(TestCase):
    def setUp(self):
        user = mommy.make(User)
        user.profile.sp_price = 100
        user.profile.save()
        self.user = User.objects.get(id=user.id)

    def test_add_plan_credit_to_developer(self):
        milestone = mommy.make(PM_Milestone)
        task = mommy.make(PM_Task, milestone=milestone, planTime=10)
        Credit().add_credit_developer(self.user, milestone, task)
        credit = Credit.objects.filter(user=self.user)
        self.assertEqual(len(credit), 1)
        self.assertEqual(credit[0].value, 1000)
        self.assertEqual(credit[0].type, '0')

    def test_add_fact_credit_to_developer(self):
        milestone = mommy.make(PM_Milestone, closed=True, final_delay=0)
        task = mommy.make(PM_Task, milestone=milestone, planTime = 10)
        Credit().add_credit_developer(self.user, milestone, task)
        credit = Credit.objects.filter(user=self.user)
        self.assertEqual(len(credit), 1)
        self.assertEqual(credit[0].value, 1000)
        self.assertEqual(credit[0].type, '1')

    def test_add_fact_credit_to_developer_w_deduction(self):
        milestone = mommy.make(PM_Milestone, closed=True, final_delay=10)
        task = mommy.make(PM_Task, milestone=milestone, planTime=10)
        Credit().add_credit_developer(self.user, milestone, task)
        credit = Credit.objects.filter(user=self.user)
        self.assertEqual(len(credit), 2)
        self.assertEqual(credit[0].value, 1000)
        self.assertEqual(credit[0].type, '1')
        self.assertEqual(credit[1].value, -1000 * 10 * 0.02)
        self.assertEqual(credit[1].type, '1')

    def test_add_plan_credit_to_manager_56(self):
        # 56 hours milestone
        milestone = mommy.make(PM_Milestone, type=PM_Milestone.TYPE_56)
        Credit().add_credit_manager(self.user, milestone)
        credit = Credit.objects.filter(user=self.user)
        self.assertEqual(len(credit), 1)
        self.assertEqual(credit[0].value, 17000)
        self.assertEqual(credit[0].type, '0')

    def test_add_plan_credit_to_manager_56(self):
        # 56 hours milestone
        milestone = mommy.make(PM_Milestone, type=PM_Milestone.TYPE_56)
        Credit().add_credit_manager(self.user, milestone)
        credit = Credit.objects.filter(user=self.user)
        self.assertEqual(len(credit), 2)
        self.assertEqual(credit[0].value, 13000)
        self.assertEqual(credit[0].type, '0')
        self.assertEqual(credit[1].value, 6000)
        self.assertEqual(credit[1].type, '0')

    def test_add_plan_credit_to_manager_56_extra(self):
        #56 hours milestone with extra hours
        milestone = mommy.make(PM_Milestone, type=PM_Milestone.TYPE_56, extra_hours=10)
        Credit().add_credit_manager(self.user, milestone)
        credit = Credit.objects.filter(user=self.user)
        self.assertEqual(len(credit), 2)
        self.assertEqual(credit[0].value, 15321)
        self.assertEqual(credit[0].type, '0')
        self.assertEqual(credit[1].value, 7071)
        self.assertEqual(credit[1].type, '0')

    def test_add_fact_credit_to_manager_56_extra(self):
        #56 hours milestone with extra hours
        milestone = mommy.make(
            PM_Milestone,
            type=PM_Milestone.TYPE_56,
            closed=True,
            extra_hours=10,
            g_factor=1,
            delay_factor=1,
        )
        Credit().add_credit_manager(self.user, milestone)
        credit = Credit.objects.filter(user=self.user)
        self.assertEqual(len(credit), 2)
        self.assertEqual(credit[0].value, 15321)
        self.assertEqual(credit[0].type, '1')
        self.assertEqual(credit[1].value, 3000)
        self.assertEqual(credit[1].type, '1')

    def test_add_fact_credit_to_manager_56_delay10(self):
        #56 hours milestone with 10 days delay
        milestone = mommy.make(
            PM_Milestone,
            type=PM_Milestone.TYPE_56,
            closed=True,
            g_factor=1,
            delay_factor=0,
        )
        Credit().add_credit_manager(self.user, milestone)
        credit = Credit.objects.filter(user=self.user)
        self.assertEqual(len(credit), 1)
        self.assertEqual(credit[0].value, 13000)
        self.assertEqual(credit[0].type, '1')

    def test_add_fact_credit_to_manager_56_delay5(self):
        #56 hours milestone with 5 days delay
        milestone = mommy.make(
            PM_Milestone,
            type=PM_Milestone.TYPE_56,
            closed=True,
            g_factor=1,
            delay_factor=0.5,
        )
        Credit().add_credit_manager(self.user, milestone)
        credit = Credit.objects.filter(user=self.user)
        self.assertEqual(len(credit), 2)
        self.assertEqual(credit[0].value, 13000)
        self.assertEqual(credit[0].type, '1')
        self.assertEqual(credit[1].value, 1500)
        self.assertEqual(credit[1].type, '1')

    def test_add_fact_credit_to_manager_56_delay2(self):
        milestone = mommy.make(
            PM_Milestone,
            type=PM_Milestone.TYPE_56,
            closed=True,
            g_factor=1,
            delay_factor=0.7,
        )
        Credit().add_credit_manager(self.user, milestone)
        credit = Credit.objects.filter(user=self.user)
        self.assertEqual(len(credit), 2)
        self.assertEqual(credit[0].value, 13000)
        self.assertEqual(credit[0].type, '1')
        self.assertEqual(credit[1].value, 2100)
        self.assertEqual(credit[1].type, '1')

    def test_add_fact_credit_to_manager_56_with_grooming(self):
        #56 hours milestone, 0 days delay, with grooming
        milestone = mommy.make(
            PM_Milestone,
            type=PM_Milestone.TYPE_56,
            closed=True,
            g_factor=1,
            delay_factor=1,
            is_has_grooming=True
        )
        Credit().add_credit_manager(self.user, milestone)
        credit = Credit.objects.filter(user=self.user)
        self.assertEqual(len(credit), 2)
        self.assertEqual(credit[0].value, 13000)
        self.assertEqual(credit[0].type, '1')
        self.assertEqual(credit[1].value, 4500)
        self.assertEqual(credit[1].type, '1')

    def test_add_fact_credit_to_manager_56_51(self):
        #56 hours milestone, 0 days delay, 51% closed
        milestone = mommy.make(
            PM_Milestone,
            type=PM_Milestone.TYPE_56,
            closed=True,
            g_factor=1,
            delay_factor=1,
            is_half_completed=True
        )
        Credit().add_credit_manager(self.user, milestone)
        credit = Credit.objects.filter(user=self.user)
        self.assertEqual(len(credit), 2)
        self.assertEqual(credit[0].value, 13000)
        self.assertEqual(credit[0].type, '1')
        self.assertEqual(credit[1].value, 4500)
        self.assertEqual(credit[1].type, '1')

    def test_add_fact_credit_to_manager_56_50(self):
        #56 hours milestone, 0 days delay, 49% closed
        milestone = mommy.make(
            PM_Milestone,
            type=PM_Milestone.TYPE_56,
            closed=True,
            g_factor=1,
            delay_factor=1,
            is_half_completed=False
        )
        Credit().add_credit_manager(self.user, milestone)
        credit = Credit.objects.filter(user=self.user)
        self.assertEqual(len(credit), 2)
        self.assertEqual(credit[0].value, 13000)
        self.assertEqual(credit[0].type, '1')
        self.assertEqual(credit[1].value, 3000)
        self.assertEqual(credit[1].type, '1')
