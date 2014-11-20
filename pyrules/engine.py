from pyrules.dictobj import DictObject


class RuleContext(DictObject):
    """
    Rule context to store values and attributes (or any object)
    
    The rule context is used to pass in attribute values that
    for the rules to consider. A rule does not have access to
    any other data except provided in this rule context. 
    """
    def __init__(self):
        super(RuleContext, self).__init__()
        self._executed=[]
    def __setitem__(self, item, value):
        self.__setattr__(item, value)
    def __getattr__(self, item):
        if not item in self.__dict__ and not item in self._data:
            return None
        return super(RuleContext, self).__getattr__(item)
    @property
    def as_dict(self):
        return {'context' : self }



class RuleEngine(object):
    """
    This basic rule engine runs through all rules in the ruleset, then:
    
    1. call each rules should_trigger method 
    2. if True, call the rule's perform method to evaluate it
    3. then call the rule's record method, to record the evaluation's result
    """
    def execute(self, ruleset, context):
        for rule in ruleset:
            if rule.should_trigger(context):
                result = rule.perform(context)
                rule.record(context, result)
        return context
