import unittest
from pyrules import DictObject, RuleContext, RuleEngine, Translator
from pyrules import Rule, ConditionalRule, TableRule


class DictObjectTest(unittest.TestCase):
    def test_initial(self):
        obj = DictObject(initial={'foo': 'bar'})
        self.assertEqual(obj.to_dict(), {'foo': 'bar'})
    
    def test_methods(self):
        obj = DictObject()
        self.assertEqual(obj.to_dict(), {})
        obj.foo = 'bar'
        self.assertEqual(obj.to_dict(), {'foo': 'bar'})
        self.assertEqual(obj.foo, 'bar')
        obj.foo1 = '123'
        self.assertEqual(obj.to_dict(), {'foo': 'bar', 'foo1': '123'})
        obj._secret = 'NOT GONNA SHOW YOU THIS'
        self.assertEqual(obj.to_dict(), {'foo': 'bar', 'foo1': '123'})
        self.assertEqual(obj._secret, 'NOT GONNA SHOW YOU THIS')


class EngineTest(unittest.TestCase):
    def test_rule_context(self):
        context = RuleContext()
        self.assertEqual(context.as_dict, {'context': context})
        self.assertEqual(context.to_dict(), {})
        context['foo'] = 'bar'
        self.assertEqual(context.to_dict(), {'foo': 'bar'})
        self.assertEqual(context.foo1, None)
        context.foo1 = '123'
        self.assertEqual(context.to_dict(), {'foo': 'bar', 'foo1': '123'})
        self.assertEqual(context.foo1, '123')

    def test_rule_engine(self):
        pass


class LanguageTest(unittest.TestCase):
    def test_translator(self):
        trans = Translator({'foo': 'bar'})
        self.assertEqual(len(trans.translations), 1)
        self.assertEqual(trans.translations[0][1:], ('foo', 'bar'))
        self.assertEqual(
            trans.replace('A foo inside this string'),
            'A bar inside this string')
        self.assertEqual(trans.replace('foo'), 'bar')
        self.assertEqual(trans.replace('foo foo foo'), 'bar bar bar')
        self.assertEqual(trans.replace('not changed'), 'not changed')



class TestRule(Rule):
    def perform(self, context):
        return 'ok'


class FareRule(ConditionalRule):
    def condition(self, context):
        return True

    def action(self, context):
        return {'fare': context.distance * 20}


class RuleTest(unittest.TestCase):
    def test_rule(self):
        rule = TestRule()
        context = RuleContext()
        self.assertTrue(rule.should_trigger(context))
        self.assertEqual(rule.perform(context), 'ok')
        self.assertEqual(rule.ruleid, 'TestRule')
        rule.record(context, 'foo')
        self.assertTrue((rule.ruleid, 'foo') in context._executed)

    def test_table_rule(self):
        rules = [
            {'if': ['not context.foo'], 'then': ['10'], 'target': ['bar']},
            {'if': ['context.foo', 'True'], 'then': ['20', '30'],
             'target': ['bar1', 'bar2']},
            {'if': ['context.foo', 'False'], 'then': ['40', '50'],
             'target': ['bar3', 'bar4']},
        ]
        trule = TableRule(rules)
        context = RuleContext({'foo': True})
        engine = RuleEngine()
        engine.execute([trule], context)
        self.assertEqual(
            context._executed,
            [('TableRule.1', 20), ('TableRule.1', 30), ('TableRule', True)])
        self.assertEqual(context.to_dict(), {'foo': True, 'bar1': 20, 'bar2': 30})

    def test_engine(self):
        translations = [
            ('das Wetter', 'context.weather'),
            ('ist', '=='),
            ('schoen', '"nice"'),
            ('Fahrpreis', 'context.fare'),
            ('Wochenende', 'context.weekend'),  
            ('nicht', 'not'),
            ('am Sonntag', 'context.sunday')
        ]
        rule_clauses = [
            {'if': ['nicht Wochenende', 'das Wetter ist schoen'],
             'then' : ['Fahrpreis * 1'],
             'target' : ['Fahrpreis']},
            {'if': ['am Sonntag', 'das Wetter ist schoen'],
             'then' : ['Fahrpreis * 1.5'],
             'target' : ['Fahrpreis']}
        ]
        trule = TableRule(rule_clauses, translations)

        context = RuleContext({
            'distance': 10, 'weekend': 0, 'weather': 'nice', 'sunday': 1})
        rules = (
            FareRule(),
            ConditionalRule(
                lambda self, context: bool(context.weekend),
                lambda self, context: {'fare': context.fare * 1.2}
            ),
            ConditionalRule(
                condition=lambda self, context: not context.weekend,
                action=lambda self, context: {'fare': context.fare * 4}),
            trule
        )
        engine = RuleEngine()
        engine.execute(rules, context)

        self.assertEqual(context.fare, 1200.0)
        self.assertEqual(
            context._executed,
            [
                ('FareRule', {'fare': 200}),
                ('ConditionalRule', {'fare': 800}),
                ('TableRule.1', 800), ('TableRule.2', 1200.0),
                ('TableRule', True)
            ])

    def test_yaml_loading(self):
        rules_string = '''
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
        '''
        trule = TableRule.from_yaml(rules_string)
        self.assertEqual(
            trule.rules,
            [
                {'rule': 'test1', 'if': ['not context.foo'], 'then': ['10'],
                 'target': ['bar']},
                {'rule': None, 'if': ['context.foo', 'True'], 'then': ['20', '30'],
                 'target': ['bar1', 'bar2']},
                {'rule': None, 'if': ['context.foo', 'False'], 'then': ['40', '50'],
                 'target': ['bar3', 'bar4']}
            ])
            
        self.assertEqual(trule.ruleid, 'TestTableRule')
        context = RuleContext({'foo': True})
        engine = RuleEngine()
        engine.execute([trule], context)
        self.assertEqual(
            context._executed,
            [('TestTableRule.1', 20), ('TestTableRule.1', 30),
             ('TestTableRule', True)])
        self.assertEqual(
            context.to_dict(), {'foo': True, 'bar1': 20, 'bar2': 30})

    def test_json_loading(self):
        rules_string = '''
{
    "ruleset": "TestTableRule",
    "rules": [
        {
            "rule": "test1",
            "if": ["not context.foo"],
            "then": ["10"],
            "target": ["bar"]
        },
        {
            "if": ["context.foo", "True"],
            "then": ["20", "30"],
            "target": ["bar1", "bar2"]
        },
        {
            "if": ["context.foo", "False"],
            "then": ["40", "50"],
            "target": ["bar3", "bar4"]
        }
    ]
}
        '''
        trule = TableRule.from_json(rules_string)
        self.assertEqual(
            trule.rules,
            [
                {'rule': 'test1', 'if': ['not context.foo'], 'then': ['10'],
                 'target': ['bar']},
                {'rule': None, 'if': ['context.foo', 'True'], 'then': ['20', '30'],
                 'target': ['bar1', 'bar2']},
                {'rule': None, 'if': ['context.foo', 'False'], 'then': ['40', '50'],
                 'target': ['bar3', 'bar4']}
            ])
            
        self.assertEqual(trule.ruleid, 'TestTableRule')
        context = RuleContext({'foo': True})
        engine = RuleEngine()
        engine.execute([trule], context)
        self.assertEqual(
            context._executed,
            [('TestTableRule.1', 20), ('TestTableRule.1', 30),
             ('TestTableRule', True)])
        self.assertEqual(
            context.to_dict(), {'foo': True, 'bar1': 20, 'bar2': 30})
        