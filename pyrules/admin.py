from django.contrib import admin
from pyrules import models


class RuleAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['name']}

admin.site.register(models.Rule, RuleAdmin)


class TableRuleAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['name']}
    exclude = 'source',

admin.site.register(models.TableRule, TableRuleAdmin)


class RulePositionAdmin(admin.TabularInline):
    model = models.RulePosition


class RulesetAdmin(admin.ModelAdmin):
    inlines = [RulePositionAdmin]


admin.site.register(models.Ruleset, RulesetAdmin)
