from serif.theory.serif_theory import SerifTheory
from serif.xmlio import _OffsetAttribute


class SerifOffsetTheory(SerifTheory):
    """Base class for theory objects that have attributes"""
    start_byte = _OffsetAttribute('start', 'byte')
    end_byte = _OffsetAttribute('end', 'byte')
    start_char = _OffsetAttribute('start', 'char')
    end_char = _OffsetAttribute('end', 'char')
    start_edt = _OffsetAttribute('start', 'edt')
    end_edt = _OffsetAttribute('end', 'edt')

    def set_offset(self, start_char, end_char):
        self.start_char = start_char
        self.end_char = end_char
        self.start_edt = start_char
        self.end_edt = end_char

    def _get_summary(self):
        text = self.text
        if text is None:
            return None
        else:
            return repr(text)

    @property
    def text(self):
        """The original text substring covered by this theory"""
        return self.get_original_text_substring(self.start_char, self.end_char)
