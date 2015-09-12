from celery import task
from . import RuleEngine, RuleStore, RuleContext


@task
def execute_rule(name, context):
    context = RuleContext(context)
    engine = RuleEngine()
    rule = RuleStore().get_rule(name)
    return {
        'result': engine.execute([rule], context).to_dict()}


@task
def execute_ruleset(name, context):
    context = RuleContext(context)
    engine = RuleEngine()
    ruleset = RuleStore().get_ruleset(name)
    return {
        'result': engine.execute(ruleset, context).to_dict()}

