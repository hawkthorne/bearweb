import json

from django.test import TestCase
from django.contrib.auth.models import User
from games.models import Game, Framework


class StackMachineViewsTests(TestCase):

    def setUp(self):
        user = User.objects.create_user("foo", "bar@example.com", "pass")
        framework = Framework.objects.create(name="Other")
        self.game = Game.objects.create(owner=user, framework=framework,
                                        name="Foo", slug="foo")
        self.base = "/api/games/{}".format(self.game.uuid)

    def test_report_metrics(self):
        metrics_url = self.base + "/metrics"

        metric = {
            'metrics': [{
                'event': 'foo',
                'properties': {'key': 'value'},
            }],
        }

        response = self.client.post(metrics_url,
                                    content_type='application/json',
                                    data=json.dumps(metric))

        self.assertEquals(response.status_code, 204)
        self.assertEquals(response['Content-Type'], 'application/json')

    def test_report_errors(self):
        errors_url = self.base + "/errors"

        error = {
            'errors': [{
                'message': 'foo',
                'tags': {
                    'os': 'windows',
                    'version': '0.0.0',
                    'distinct_id': 'foo'
                },
            }],
        }

        response = self.client.post(errors_url,
                                    content_type='application/json',
                                    data=json.dumps(error))

        self.assertEquals(response.status_code, 204)
        self.assertEquals(response['Content-Type'], 'application/json')

    def test_appcast(self):
        response = self.client.get(self.base + "/appcast")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response['Content-Type'], 'application/json')
