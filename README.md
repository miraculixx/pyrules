pyrules
=======

Python Rules Engine

This is a first go at implementing a generic Rule Engine in Python.

What you can do with it
-----------------------

See `sample.py` for a complete sample.

*Basic example*

1. Define simple rules

``` python
class CalculateBasicFare(Rule):
    def should_trigger(self, context):
        return True
    def perform(self, context):
        context.fare = context.distance * 20
        return context.fare
        
class CalculateWeekendFare(Rule):
    def should_trigger(self, context):
        return context.weekend 
    def perform(self, context):
        context.fare = context.fare * 1.2
        return context.fare 
```

2. Define a ruleset

``` python
ruleset = (
  CalculateBasicFare(),
  CalculateWeekendFare(),
)
```

3. Define the context

The rule context is the set of data the rules will operate on. Within a rule, the context is available as the `context` variable.

``` python
context = RuleContext()
context.distance = 10
context.weekend = 0
context.sunday = 1
```

4. Execute the rules

This will execute the rules defined in the ruleset. The results will be stored in the context (it is up to the rules to set the respective context attribute).

``` python
engine = RuleEngine()
context = engine.execute(ruleset, context)
print "fare", context.fare
print "executed", context._executed
```

### Advanced features

*SequencedRuleset*

A `SequencedRuleset` ensures that rules are executed in sequence:

```
ruleset = (
   SequencedRuleset([CalculateBasicFare(), CalculateWeekendFare()]),
)
```

*TableRuleset*

A `TableRuleset`  is defined by a list of rules given in the following form. Note that the list of conditions (`if`) are
must all be met for the rule to trigger (logical AND). If the rule triggers, each action _i_ ( `then`) is executed and
its result stored in the corresponding _ith_ context variable (`target`).

```
manyrules = TableRuleset([
  { 'if': ['not weekend'],
    'then' : ['fare * 1'],
    'target' : ['fare'],
  },
  { 'if': ['not sunday'],
    'then' : ['fare * 1.5'],
    'target' : ['fare'],
  }
])
```

Add `manyrules` to the ruleset, just as you would with any other `Rule` instance:

```
ruleset = (CalculateBasicFare(),
           CalculateWeekendFare(),
           manyrules,
)
```

*Natural language rules*

`TableRuleset` offers a translation feature that can translate natural-language rules (somewhat) into executable rules:

``` python
translations=[
  ('the weather', 'context.weather'),
  ('is', '=='),
  ('nice', '"nice"'),
  ('Fare', 'context.fare'),
  ('weekend', 'context.weekend'),  
  ('not', 'not'),
  ('on Sunday', 'context.sunday'),
]

manyrules = TableRuleset([
  { 'if': ['not weekend', 'the weather is nice'],
    'then' : ['Fare * 1'],
    'target' : ['Fare'],
  },
  { 'if': ['on Sunday', 'the weather is nice'],
    'then' : ['Fare * 1.5'],
    'target' : ['Fare'],
  }
], translations=translations)
```

### How to contribute

All contributes are welcome! Please have a look at the list of issues. If you find a bug, please open a new issue. 
If you contribute code or fixes, please create a pull-request. Thanks.
