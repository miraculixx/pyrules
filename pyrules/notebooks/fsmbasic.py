# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

class NoTransitionForEvent(Exception):
    pass

class Transition(object):
    def __init__(self, fsm=None, from_state_id=None, to_state_id=None, event=None, condition=None):
        assert isinstance(fsm, FSM), "need to assign an FSM"
        assert from_state_id, "need to specify a from_state_id"
        assert to_state_id, "need to specify a to_state_id"
        assert event or condition, "need to specify an event or a condition"
        self.from_state_id = from_state_id
        self.to_state_id = to_state_id
        self.event = event
        self.condition = condition
        self.fsm=fsm
    
    def should_transition(self, event):
        if self.event and self.event == event:
            return True
        elif self.condition:
            return self.condition_matched(event)
        return False
        
    def condition_matched(self, event):
        return self.condition(self, event)
    
    @property
    def next(self):
        return self.to_state_id
    
    def __repr__(self):
        return "Transition from %s to %s on event %s or condition %s" % (self.from_state_id, self.to_state_id, 
                                                                         self.event, self.condition)
        
class State(object):
    def __init__(self, fsm, state_id, subfsm=None, on_entry=None, on_exit=None):
        assert isinstance(fsm, FSM), "must provide an fsm"
        assert state_id, "must provide an state_id"
        self.fsm = fsm
        self.state_id = state_id
        self.subfsm = subfsm
        self.on_entry = on_entry
        self.on_exit = on_exit
        self.transitions = []
        
    def addTransition(self, transition):
        self.transitions.append(transition)
        return self
    
    def enter(self, event, transition):
        if self.on_entry: 
            self.on_entry(self, event, transition)
            
    def leave(self, event, transition):
        if self.on_exit:
            self.on_exit(self, event, transition)
    
    def __repr__(self):
        return "State %s" % self.state_id
    
class FSM(object):
    def __init__(self, initial_state_id=None):
        self.states = {}
        self.current = None
        self.initial_state_id = initial_state_id
    
    def addState(self, state_id, subfsm=None, on_entry=None, on_exit=None):
        self.states[state_id] = State(self, state_id, on_entry=on_entry, on_exit=on_exit)
        if not self.initial_state_id:
            self.initial_state_id = state_id
        return self
        
    def addTransition(self, from_state_id, to_state_id, event=None, condition=None):
        t = Transition(self, from_state_id, to_state_id, event=event, condition=condition)
        state = self.state_from_id(t.from_state_id)
        state.addTransition(t)
        return self
    
    def state_from_id(self, state_id):
        try:
            return self.states[state_id]
        except KeyError as e:
            raise KeyError("No state >%s<" % state_id)
    
    @property
    def initial_state(self):
        return self.state_from_id(self.initial_state_id)
    
    @property
    def state(self):
        if not self.current:
            self.current = self.initial_state
        return self.current
    
    def process(self, event):
        self.current = self.state
        if self.current:
            did_transition = False
            for t in self.current.transitions:
                if t.should_transition(event):
                    print t
                    self.current = self.state_from_id(t.next)
                    did_transition = True
            if not did_transition:
                raise NoTransitionForEvent("from %s on %s" % (self.current, event))
        return self.current

from pyrules.engine import RuleContext, RuleEngine
from pyrules.rules import Rule, TableRuleset, LambdaRule    
    
class RulesetCondition(object):
    """
    a transition condition that uses a ruleset to determine the 
    """
    def __init__(self, engine, ruleset):
        self.engine = engine
        self.ruleset = ruleset
      
    def __call__(self, fsm, event):
        """ 
        the condition function is called by fsm.should_transition()
        The ruleset should return True if the event should allowed the
        transition
        
        :param return: True if transition is allowed 
        """
        context = RuleContext()
        context.event = event
        self.fsm = fsm
        self.engine.execute(self.ruleset, context)
        return len(context._executed) == len(self.ruleset) and all([result for rule, result in context._executed])
        
        

# <codecell>

fsm = FSM()
fsm.addState("requested")
fsm.addState("confirmed")
fsm.addState("cancelled")
fsm.addState("pending")

class SomeRule(LambdaRule):
    condition = lambda s, ctx: True
    action = lambda s, ctx: { 'result' : True }

class SomeOtherRule(LambdaRule):
    condition = lambda s, ctx: False
    action = lambda s, ctx: { 'result' : True }
    
engine = RuleEngine()
    
ruleset = (
   SomeRule(),
   SomeOtherRule(),
)

ruleset_condition = RulesetCondition(engine, ruleset)

print fsm.state
fsm.addTransition("requested", "pending", condition=ruleset_condition)
fsm.process("pending")



# <codecell>

fsm = FSM()
fsm.addState("requested")
fsm.addState("confirmed")
fsm.addState("cancelled")
fsm.addState("pending")
fsm.addTransition("requested", "pending", "order")
fsm.addTransition("pending", "confirmed", "payed")
fsm.addTransition("requested", "confirmed", "payed")
fsm.addTransition("confirmed", "cancelled", condition=lambda t,event : event == "cancel")
print fsm.process("order")
print fsm.process("payed")
print fsm.process("cancel")

# <markdowncell>

# How to make this efficient with Django models
# ============================================
# 
# FSMModel Django model
# => holds the model definition
# => holds the States
# => States hold the transitions
# => transitions hold the rulesets to execute
# 
# FSMInstance Django model
# => holds the current state + data for this FSM
# 
# On event:
# 1. load the FSMInstance given the FSM id 
# 2. load the current state and all its transitions
# 3. load the associated data
# 4. load all Rulesets associated with the FSM
# 5. process the event (execute rulesets)
# 6. execute any callbacks necessary
# 
# => no need to hold any data in memory longer than actually required
# => can process FSMInstances at scale easily (through Celery workers, database sharding)
# => will execute callbacks efficiently (through Celery tasks)
# 

# <codecell>

fsm.state_from_id("confirmed").transitions

