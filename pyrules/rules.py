from pyrules.dictobj import DictObject
from pyrules.language import Translator
     
class Rule(object):
    """
    basic rule
    """
    def should_trigger(self, context):
        pass
    def perform(self, context):
        pass
    def record(self, context, result):
        context._executed.append((self.ruleid, result))
    @property
    def ruleid(self):
        return self.__class__.__name__.split('.')[-1]
    
class LambdaRule(Rule):
    """
    LambdaRules define two class-variable lambdas: condition and action
    
    condition = lambda self, context: <some condition returning True or False>
    action = lambda self, context: <return a dict to update the context with>
    
    Example:
    
    class MyLambdaRule(Rule):
        # always run and return 5
        condition = lambda self, context: True
        action = lambda self, context: { 'result': 5 }
    """
    condition = lambda self, context: False
    action = lambda self, context: None 
    def should_trigger(self, context):
        return self.condition(context)
    def perform(self, context):
        result = self.action(context) 
        context.update(result)
        return result
    
class TableRuleset(Rule):
    """
    a table ruleset created from a list of dict objects of the following format
    
    [ 
      {
        'if' : ['condition1', ...],
        'then' : ['action1', ...],
        'target' : ['target1', ...]
      }, 
      ...
    ]
    
    Each rule is only executed if all conditions are met. In conditions and actions, use context. 
    to reference variables. targets implicitly reference context. (target 'xy' means 'context.xy').
    The result of the nth 'then' action is stored in the nth context.variable as defined in target.
    """
    def __init__(self, rules, translations=None):
        self.rules = rules or {}
        if translations:
            translator = Translator(translations)
            for rule in self.rules:
                for key in rule.keys():
                    rule[key] = [translator.replace(item) for item in rule[key]]
    def should_trigger(self, context):
        return True
    def perform(self, context):
        count = 0
        for rule in self.rules:
            if all([eval(condition, context.as_dict) for condition in rule['if']]):
                count = count + 1
                self._current_ruleid = rule.get('id', count)
                for action, target in zip(rule['then'], rule['target']):
                    if context._translations:
                        action = context._translations.replace(action)
                        target = context._translations.replace(target)
                    result = context[target.replace('context.', '').strip()] = eval(action, context.as_dict)
                    self.record(context, result)
            else:
                break
        else:
            self._current_ruleid = None
            return True
        return False
    @property
    def ruleid(self):
        if self._current_ruleid:
            return "%s.%s" % (super(TableRuleset, self).ruleid, self._current_ruleid)
        return super(TableRuleset, self).ruleid
    

    
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
    
class NaturalLanguageRule(TableRuleset):
    """
    A natural language rule given as a text. 
    TODO implement this
    """
    def __init__(self, translations):
        translator = Translator(translations)
        from inspect import getdoc
            
    def should_trigger(self, context):
        pass
        
