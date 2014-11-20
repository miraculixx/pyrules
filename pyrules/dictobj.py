'''
Created on Oct 15, 2013

@author: patrick
'''
class DictObject(object):
    """
    Simple object that stores all attributes
    in a dict
    """
    def __init__(self, initial=None):
        self.__dict__['_data'] = {}
        if initial:
            self.update(initial)

    def __getattr__(self, name):
        return self._data.get(name, None)

    def __setattr__(self, name, value):
        #logger.debug('*********** set value %s=%s' % (name, value))
        self.__dict__['_data'][name] = value
        
    def update(self, other):
        for k in other:
            self.__setattr__(k, other[k])

    def to_dict(self):
        return self._data
    
    