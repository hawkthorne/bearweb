from django.test import TestCase

from django.contrib.auth.models import User
from core.models import Subscription


class CoreModelTests(TestCase):

    def test_subscriptions(self):
        user = User.objects.create_user("foo", "bar@example.com", "pass")
        s = Subscription.display_name_for(user)
        self.assertEquals("free", s)
        user.subscription_set.create(plan="premium")
        s = Subscription.display_name_for(user)
        self.assertEquals("premium", s)
