from django.test import TestCase

from django.contrib.auth.models import User


class CoreModelTests(TestCase):

    def test_subscriptions(self):
        self.assertEquals(2, 1 + 1)
