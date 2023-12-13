class FieldTranslation:
    def __init__(self, original, translation, translator=None, reverse_translator=None):
        self.original = original
        self.translation = translation
        self.translator = translator
        self.reverse_translator = reverse_translator

    def translate(self, field_value):
        if self.translator is None:
            return field_value
        return self.translator(field_value)

    def reverse_translate(self, field_value):
        if self.reverse_translator is None:
            return field_value
        return self.reverse_translator(field_value)