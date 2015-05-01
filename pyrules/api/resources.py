import json
from tastypie.resources import Resource
from .. import RuleEngine, RuleStore, RuleContext


class RuleSyncResource(Resource):
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


class RulesetSyncResource(Resource):
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
