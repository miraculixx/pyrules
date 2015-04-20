class BaseStorage(object):
    def get_rule(self, name):
        raise NotImplementedError()

    def get_ruleset(self, name):
        raise NotImplementedError()
