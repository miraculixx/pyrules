class Translator(object):
    """
    a simple translator. It takes a list of translations in the format
    
    [
      (source, target),
      ...
    ]
    
    as the constructor input. on calling .replace(input) it will translate
    any word from input according to the translations given.
    """
    def __init__(self, translations):
        self.translations = translations
    def replace(self, input):
        input = " %s " % input
        for source, target in self.translations:
            input = input.replace(" %s" % source, " %s " % target)
        return input
    
