import time
from django.contrib.auth.models import User
from django.db.models.loading import cache
from django.test import TestCase
from django.test.client import Client
from django.test.testcases import TransactionTestCase
from tastypie.test import ResourceTestCase


class TransactionResourceTestCase(ResourceTestCase):
    def _fixture_setup(self):
        return TransactionTestCase._fixture_setup(self)

    def _fixture_teardown(self):
        return TransactionTestCase._fixture_teardown(self)


class ResourceTestCase(TransactionResourceTestCase):
    fixtures = ['examples/sample/sampleapp/fixtures/sample.json']

    def test_sync_rule(self):
        data = {'first': 30, 'second': 3}
        response = self.api_client.post(
            '/api/v1/rule/first/', data=data)
        self.assertEqual(
            self.deserialize(response),
            {'resource_uri': '/api/v1/rule/first/',
             'result': {
                 'first': 30, 'second': 3, 'double_first': 60}})

    def test_async_rule(self):
        data = {'first': 30, 'second': 3}
        response = self.api_client.post(
            '/api/v1/rule_async/first/', data=data)
        # Get state location
        self.assertHttpAccepted(response)
        state_url = response['Location']
        time.sleep(2)
        # Get state - should be ready.
        response = self.api_client.get(state_url)
        self.assertHttpOK(response)
        data = self.deserialize(response)
        self.assertEqual(data['state'], 'SUCCESS')
        # Get results at last
        response = self.api_client.get(data['result_uri'])
        self.assertHttpOK(response)
        data = self.deserialize(response)
        self.assertEqual(
            data['result'],
            {'first': 30, 'second': 3, 'double_first': 60})

    def test_sync_ruleset(self):
        data = {'first': 30, 'second': 3}
        response = self.api_client.post(
            '/api/v1/ruleset/Sample/', data=data)
        data = self.deserialize(response)
        self.assertEqual(
            data,
            {'resource_uri': '/api/v1/ruleset/Sample/',
             'result': {
                 'first': 30, 'second': 3, 'double_first': 60,
                 'div_result': 10}})

    def test_async_ruleset(self):
        data = {'first': 30, 'second': 3}
        response = self.api_client.post(
            '/api/v1/ruleset_async/Sample/', data=data)
        # Get state location
        self.assertHttpAccepted(response)
        state_url = response['Location']
        time.sleep(2)
        # Get state - should be ready.
        response = self.api_client.get(state_url)
        self.assertHttpOK(response)
        data = self.deserialize(response)
        self.assertEqual(data['state'], 'SUCCESS')
        # Get results at last
        response = self.api_client.get(data['result_uri'])
        self.assertHttpOK(response)
        data = self.deserialize(response)
        self.assertEqual(
            data['result'],
            {'first': 30, 'second': 3, 'double_first': 60, 'div_result': 10})
