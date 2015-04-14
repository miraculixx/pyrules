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
        self._data = {}
        if initial:
            self.update(initial)

    def __getattr__(self, name):
        """
        This method is only called when python can't find attribute via
        normal attr lookup. So if it's not in our _data dictionary, it's not
        set.
        """
        return self._data.get(name)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            object.__setattr__(self, name, value)
        else:
            self.__dict__['_data'][name] = value
        
    def update(self, other):
        for k in other:
            self.__setattr__(k, other[k])

    def to_dict(self):
        return self._data
    
    