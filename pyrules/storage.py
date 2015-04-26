from django.conf import settings
from django.utils.module_loading import import_by_path


class RuleStore(object):
    def __init__(self, backend=None):
        backend = backend or getattr(
            settings, 'PYRULES_STORAGE',
            'pyrules.storages.django.DjangoStorage')
        self.storage = import_by_path(backend)()

    def get_rule(self, name):
        return self.storage.get_rule(name)
            
    def get_ruleset(self, name):
        return self.storage.get_ruleset(name)