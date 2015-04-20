import reversion
from django.db import models


@reversion.register
class Rule(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    source = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.name


@reversion.register
class TableRule(Rule):
    TF_JSON, TF_YAML = range(2)    
    TABLE_FORMATS = (
        (TF_JSON, 'JSON'), (TF_YAML, 'YAML')
    )

    definition = models.TextField()
    tablerule_format = models.PositiveSmallIntegerField(
        choices=TABLE_FORMATS, default=TF_YAML)


class RulePosition(models.Model):
    rule = models.ForeignKey(Rule, related_name='rule_positions')
    ruleset = models.ForeignKey('Ruleset', related_name='rule_positions')
    priority = models.PositiveIntegerField()

    class Meta:
        unique_together = (
            ('rule', 'ruleset'), ('ruleset', 'priority')
        )
        ordering = 'ruleset', '-priority'

    def __unicode__(self):
        return u'{self.ruleset.name}[{self.priority}]({self.rule.name})'.format(
            self=self)


@reversion.register
class Ruleset(models.Model):
    rules = models.ManyToManyField(
        Rule, through=RulePosition, related_name='rulesets')
    name = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return self.name