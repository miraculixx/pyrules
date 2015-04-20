from __future__ import absolute_import
from django.utils.module_loading import import_by_path
from . import base
from .. import models, rules


class DjangoStorage(base.BaseStorage):
    def get_rule(self, rule):
        if isinstance(rule, basestring):
            rule = models.Rule.objects.get(slug=rule)
        try:
            trule = rule.tablerule
            text = trule.definition
            if trule.tablerule_format == models.TableRule.TF_JSON:
                rule_obj = rules.TableRule.from_json(text)
            elif trule.tablerule_format == models.TableRule.TF_YAML:
                rule_obj = rules.TableRule.from_yaml(text)
            else:
                raise NotImplementedError('Unknown format')            
        except models.TableRule.DoesNotExist:
            rule_obj = import_by_path(rule.source)()
            rule_obj.name = rule.name
        return rule_obj

    def get_ruleset(self, name):
        ruleset = models.Ruleset.objects.get(name=name)
        return [
            self.get_rule(rule_pos.rule) for rule_pos in
            ruleset.rule_positions.all()]