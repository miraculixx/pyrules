import json
import yaml
from pyrules.dictobj import DictObject
from pyrules.language import Translator
     
class Rule(object):
    """
    Base rule
    """
    name = None

    def should_trigger(self, context):
        return True

    def perform(self, context):
        raise NotImplementedError

    def record(self, context, result):
        context._executed.append((self.ruleid, result))

    @property
    def ruleid(self):
        return self.name or self.__class__.__name__.rsplit('.', 1)[-1]


class ConditionalRule(Rule):
    """
    ConditionalRule defines receives two functions as parameters: condition and
    action.
    
    @param condition: lambda context: <some condition returning True or False>
    @param action: lambda context: <return a dict to update the context with>
    
    Example:
    
    >>> rule = ConditionalRule(
    ...     condition=lambda context: True,
    ...     action=lambda context: {'result': 5})
    """
    def __init__(self, condition=None, action=None):
        self._condition = condition
        self._action = action

    def condition(self, context):
        """
        Condition for executing this rule.

        Override in subclasses if necessary. Should return boolean value that
        determines if rule is used.
        """
        return self._condition(self, context)

    def action(self, context):
        """
        Action for executing this rule.

        Override in subclasses if necessary. Should return dictionary with
        results that will be added to context.
        """
        return self._action(self, context)

    def should_trigger(self, context):
        return self.condition(context)

    def perform(self, context):
        result = self.action(context) 
        context.update(result)
        return result


class TableRule(Rule):
    """
    A table rule is created from a list of dict objects of the following format:
    
    [ 
      {
        'if' : ['condition1', ...],
        'then' : ['action1', ...],
        'target' : ['target1', ...]
      }, 
      ...
    ]
    
    Each rule is only executed if all conditions are met. In conditions and
    actions, use 'context.' to reference variables. Targets implicitly reference
    'context.' (target 'xy' means 'context.xy').

    The result of the nth 'then' action is stored in the nth 'context.variable'
    as defined in target.
    """
    def __init__(self, rules, translations=None, name=None):
        self.rules = rules or {}
        if name:
            self.name = name
        self._current_ruleid = None
        if translations:
            translator = Translator(translations)
            for rule in self.rules:
                for key in rule.keys():
                    rule[key] = [translator.replace(item) for item in rule[key]]

    def perform(self, context):
        count = 0
        for rule in self.rules:
            if all([eval(condition, context.as_dict) for condition in rule['if']]):
                count = count + 1
                self._current_ruleid = rule.get('rule') or count
                for action, target in zip(rule['then'], rule['target']):
                    if context._translations:
                        action = context._translations.replace(action)
                        target = context._translations.replace(target)
                    result = \
                        context[target.replace('context.', '').strip()] = \
                        eval(action, context.as_dict)
                    self.record(context, result)
            else:
                continue
        else:
            self._current_ruleid = None
            return True
        return False

    @property
    def ruleid(self):
        if self._current_ruleid:
            return "%s.%s" % (super(TableRule, self).ruleid, self._current_ruleid)
        return super(TableRule, self).ruleid

    @classmethod
    def from_yaml(cls, text):
        return cls._from_data(yaml.load(text))
        
    @classmethod
    def from_json(cls, text):
        return cls._from_data(json.loads(text))

    @classmethod
    def _from_data(cls, data):
        # We have to convert non-string data in clauses back to strings,
        # because they will be eval-ed
        rules = [
            {'rule': rule.get('rule'), 'if': map(str, rule['if']),
             'then': map(str, rule['then']),
             'target': map(str, rule['target'])}
            for rule in data['rules']]
        return cls(rules, name=data.get('ruleset'))

    
class SequencedRuleset(Rule):
    """
    A set of Rules, guaranteed to run in sequence
    """
    def __init__(self, rules):
        self.rules = rules or []

    def should_trigger(self, context):
        return True

    def perform(self, context):
        for rule in self.rules:
            if rule.should_trigger(context):
                result = rule.perform(context)
                rule.record(context, result)
        return True


class NaturalLanguageRule(TableRule):
    """
    A natural language rule given as a text. 
    TODO implement this
    """
    def __init__(self, translations):
        translator = Translator(translations)
        from inspect import getdoc
            
    def should_trigger(self, context):
        pass
        
