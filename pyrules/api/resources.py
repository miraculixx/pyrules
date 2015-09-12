import json
from tastypie.resources import Resource
from tpasync.resources import AsyncResourceMixin
from .. import RuleEngine, RuleStore, RuleContext
from ..tasks import execute_rule, execute_ruleset


class RuleSyncResourceMixin(object):
    class Meta:
        allowed_methods = ['post']
        resource_name = 'rule'
        include_resource_uri = False

    def post_detail(self, request, pk, **kwargs):
        try:
            engine = self._engine
        except AttributeError:
            engine = RuleEngine()
            self._engine = engine

        context = RuleContext(json.loads(request.body))
        rule = RuleStore().get_rule(pk)
        data = {
            'result': engine.execute([rule], context).to_dict(),
            'resource_uri': '/api/{}/rule/{}/'.format(
                kwargs['api_name'], pk)}
        bundle = self.build_bundle(data=data, obj=rule, request=request)
        self.full_dehydrate(bundle)
        return self.create_response(request, bundle)        


class RuleSyncResource(RuleSyncResourceMixin, Resource):
    pass


class RuleAsyncResourceMixin(AsyncResourceMixin):
    class Meta:
        allowed_methods = ['post']
        resource_name = 'rule_async'
        include_resource_uri = False

    def async_post_detail(self, request, pk, **kwargs):
        context = json.loads(request.body)
        return execute_rule.apply_async([pk, context])


class RuleAsyncResource(RuleAsyncResourceMixin, Resource):
    pass


class RulesetSyncResourceMixin(object):
    class Meta:
        allowed_methods = ['post']
        resource_name = 'ruleset'
        include_resource_uri = False

    def post_detail(self, request, pk, **kwargs):
        context = RuleContext(json.loads(request.body))
        ruleset = RuleStore().get_ruleset(pk)
        data = {
            'result': RuleEngine().execute(ruleset, context).to_dict(),
            'resource_uri': '/api/{}/ruleset/{}/'.format(
                kwargs['api_name'], pk)}
        bundle = self.build_bundle(data=data, request=request)
        self.full_dehydrate(bundle)
        return self.create_response(request, bundle)


class RulesetSyncResource(RulesetSyncResourceMixin, Resource):
    pass


class RulesetAsyncResourceMixin(AsyncResourceMixin):
    class Meta:
        allowed_methods = ['post']
        resource_name = 'ruleset_async'
        include_resource_uri = False

    def async_post_detail(self, request, pk, **kwargs):
        context = json.loads(request.body)
        return execute_ruleset.apply_async([pk, context])


class RulesetAsyncResource(RulesetAsyncResourceMixin, Resource):
    pass
