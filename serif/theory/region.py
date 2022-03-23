from serif.theory.serif_offset_theory import SerifOffsetTheory
from serif.xmlio import _ChildTextElement, _SimpleAttribute


class Region(SerifOffsetTheory):
    contents = _ChildTextElement('Contents')
    tag = _SimpleAttribute()  # is_required=True)
    is_speaker = _SimpleAttribute(bool, default=False)
    is_receiver = _SimpleAttribute(bool, default=False)

    @classmethod
    def from_values(cls, owner=None, start_char=0, end_char=0, tag=None):
        ret = cls(owner=owner)
        ret.set_offset(start_char, end_char)
        if tag is not None:
            ret.tag = tag
        return ret
