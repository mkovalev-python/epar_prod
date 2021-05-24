from django.contrib.auth.models import User
from django.test import TestCase
from model_mommy import mommy

from PManager.models import PM_ProjectRoles, PM_Project, PM_Role


class PM_ProjectTestCase(TestCase):
    def test_create_project(self):
        mommy.make(User, is_superuser=False)
        user = mommy.make(User, is_superuser=True)
        role = mommy.make(PM_Role, code='manager')
        project = mommy.make(PM_Project, )
        users = project.getUsers()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0], user)
        project.save()

    def test_get_users(self):
        project = mommy.make(PM_Project)
        user1 = mommy.make(User)
        user2 = mommy.make(User)
        mommy.make(PM_ProjectRoles, project=project, user=user1)
        with self.assertNumQueries(1):
            users = project.getUsers()
            self.assertEqual(len(users), 1)
            self.assertEqual(users[0], user1)
