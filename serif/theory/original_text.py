import sys,re

from serif.theory.serif_offset_theory import SerifOffsetTheory
from serif.xmlio import _SimpleAttribute, _ChildTextElement


def get_patterns_for_illegal_xml_unicode_char():
    # https://stackoverflow.com/a/22273639/6254393
    _illegal_unichrs = [(0x00, 0x08), (0x0B, 0x0C), (0x0E, 0x1F),
                            (0x7F, 0x84), (0x86, 0x9F),
                            (0xFDD0, 0xFDDF), (0xFFFE, 0xFFFF)]
    if sys.maxunicode >= 0x10000:  # not narrow build
            _illegal_unichrs.extend([(0x1FFFE, 0x1FFFF), (0x2FFFE, 0x2FFFF),
                                     (0x3FFFE, 0x3FFFF), (0x4FFFE, 0x4FFFF),
                                     (0x5FFFE, 0x5FFFF), (0x6FFFE, 0x6FFFF),
                                     (0x7FFFE, 0x7FFFF), (0x8FFFE, 0x8FFFF),
                                     (0x9FFFE, 0x9FFFF), (0xAFFFE, 0xAFFFF),
                                     (0xBFFFE, 0xBFFFF), (0xCFFFE, 0xCFFFF),
                                     (0xDFFFE, 0xDFFFF), (0xEFFFE, 0xEFFFF),
                                     (0xFFFFE, 0xFFFFF), (0x10FFFE, 0x10FFFF)])

    _illegal_ranges = ["%s-%s" % (chr(low), chr(high))
                       for (low, high) in _illegal_unichrs]
    _illegal_xml_chars_RE = re.compile(u'[%s]' % u''.join(_illegal_ranges))
    return _illegal_xml_chars_RE


class OriginalText(SerifOffsetTheory):
    contents = _ChildTextElement('Contents')
    href = _SimpleAttribute()

    @classmethod
    def from_values(cls, owner=None, start_char=0, end_char=0, text=""):
        ret = cls(owner=owner)
        illegal_re = get_patterns_for_illegal_xml_unicode_char()
        text = " ".join(illegal_re.split(text))
        ret.set_offset(start_char, end_char)
        ret.set_text(text)
        return ret

    def set_text(self, text):
        self.contents = text
