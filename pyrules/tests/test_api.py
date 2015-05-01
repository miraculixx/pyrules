import json
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.loading import cache
from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings
from tastypie.test import ResourceTestCase


cache.loaded = False


@override_settings(
    INSTALLED_APPS=list(
        settings.INSTALLED_APPS) + ['examples.sample.sampleapp'])
class ResourceTestCase(ResourceTestCase):
    fixtures = ['sample.json']

    def setUp(self):
        self.admin = User.objects.create_user(
            'admin', 'admin@example.com', 'topsecret')
        self.admin.is_staff = True
        self.admin.is_superuser = True
        self.admin.save()
        self.client = Client()
        self.client.login(username='admin', password='topsecret')

    def tearDown(self):
        cache.loaded = False

    def test_sync_rule(self):
        data = {'first': 30, 'second': 3}
        response = self.client.post(
            '/api/v1/rule/first/', data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(
            json.loads(response.content),
            {'resource_uri': '/api/v1/rule/first/',
             'result': {
                 'first': 30, 'second': 3, 'double_first': 60}})

    def test_async_rule(self):
        pass

    def test_sync_ruleset(self):
        data = {'first': 30, 'second': 3}
        response = self.client.post(
            '/api/v1/ruleset/Sample/', data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(
            json.loads(response.content),
            {'resource_uri': '/api/v1/ruleset/Sample/',
             'result': {
                 'first': 30, 'second': 3, 'double_first': 60,
                 'div_result': 10}})

    def test_async_ruleset(self):
        pass
