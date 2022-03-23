from serif.theory.serif_offset_theory import SerifOffsetTheory
from serif.xmlio import _SimpleAttribute


class Span(SerifOffsetTheory):
    span_type = _SimpleAttribute(is_required=True)
    region_type = _SimpleAttribute()
    idf_type = _SimpleAttribute()
    idf_role = _SimpleAttribute()
    original_sentence_index = _SimpleAttribute(int)  # For ICEWS_Sentence

    @classmethod
    def from_values(cls, owner=None, start_char=0, end_char=0, span_type="", region_type=""):
        ret = cls(owner=owner)
        ret.set_offset(start_char, end_char)
        ret.set_span_type(span_type)
        ret.set_region_type(region_type)
        return ret

    def set_span_type(self, span_type):
        self.span_type = span_type

    def set_region_type(self, region_type):
        self.region_type = region_type
