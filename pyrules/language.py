class Translator(object):
    def __init__(self, translations):
        self.translations = translations
    def replace(self, input):
        input = " %s " % input
        for source, target in self.translations:
            input = input.replace(" %s" % source, " %s " % target)
        return input
    
