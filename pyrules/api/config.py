from tastypie.api import Api
from . import resources


pr_v1 = Api(api_name='v1')
pr_v1.register(resources.RuleSyncResource())
pr_v1.register(resources.RulesetSyncResource())
