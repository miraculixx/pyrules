import re


class Translator(object):
    def __init__(self, translations):
        """
        @param translations: dict or list of translation pairs.
        """
        if isinstance(translations, dict):
            translations = translations.items()
        self.translations = [
            (re.compile(r'\b{}\b'.format(key)), key, value)
            for key, value in translations]

    def replace(self, input):
        # We use regex substitution here, since earlier implementation didn't
        # work correctly if there are overlapping strings, i.e. doing
        # ' foo foo '.replace(' foo ', ' bar ') gives just ' bar foo '
        for source, _source_text, target in self.translations:
            input = source.sub(target, input)
        return input
