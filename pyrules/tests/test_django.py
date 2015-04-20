import unittest
from django.contrib.auth.models import User
from django.test.client import Client
from .. import models, rules, storage


class DjangoAppTestCase(unittest.TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            'admin', 'admin@example.com', 'topsecret')
        self.admin.is_staff = True
        self.admin.is_superuser = True
        self.admin.save()
        self.client = Client()
        self.client.login(username='admin', password='topsecret')

    def tearDown(self):
        self.client.logout()

    def test_models(self):
        """
        Test django models.
        """
        # Create rule
        rule = models.Rule.objects.create(
            name='TestRule', slug='testrule', source='pyrules.rules.Rule')
        self.assertEqual(unicode(rule), 'TestRule')
        # Create table rule
        trule = models.TableRule.objects.create(
            name='TestTableRule', slug='test-table-rule',
            tablerule_format=models.TableRule.TF_YAML,
            definition='''
ruleset: TestTableRule
rules:  
    - rule: test1
      if:
         - not context.foo
      then:
          - 10
      target:
          - bar
    - if:
          - context.foo
          - True
      then:
          - 20
          - 30
      target:
          - bar1
          - bar2
    - if:
          - context.foo
          - False
      then:
          - 40
          - 50
      target:
          - bar3
          - bar4
            ''')
        self.assertEqual(unicode(trule), 'TestTableRule')
        # Create ruleset
        ruleset = models.Ruleset.objects.create(name='TestRuleset')
        self.assertEqual(unicode(ruleset), u'TestRuleset')
        # Create rule positions
        models.RulePosition.objects.create(
            rule=rule, ruleset=ruleset, priority=100)
        models.RulePosition.objects.create(
            rule=trule, ruleset=ruleset, priority=200)
        # Test django storage.
        # Normal rule:
        store = storage.RuleStore(
            backend='pyrules.storages.django.DjangoStorage')
        rule_obj = store.get_rule('testrule')
        self.assertEqual(rule_obj.name, 'TestRule')
        self.assertTrue(isinstance(rule_obj, rules.Rule))
        # Table rule:
        trule_obj = store.get_rule('test-table-rule')
        self.assertEqual(trule_obj.name, 'TestTableRule')
        self.assertTrue(isinstance(trule_obj, rules.TableRule))
        self.assertEqual(
            trule_obj.rules,
            [
                {'rule': 'test1', 'if': ['not context.foo'], 'then': ['10'],
                 'target': ['bar']},
                {'rule': None, 'if': ['context.foo', 'True'], 'then': ['20', '30'],
                 'target': ['bar1', 'bar2']},
                {'rule': None, 'if': ['context.foo', 'False'], 'then': ['40', '50'],
                 'target': ['bar3', 'bar4']}
            ])
        # Test ruleset API
        ruleset = store.get_ruleset('TestRuleset')
        self.assertEqual(len(ruleset), 2)
        self.assertEqual(ruleset[0].rules, trule_obj.rules)
        self.assertEqual(ruleset[0].name, trule_obj.name)
        self.assertEqual(ruleset[1].name, rule_obj.name)