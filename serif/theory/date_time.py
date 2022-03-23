from serif.theory.serif_offset_theory import SerifOffsetTheory


class DateTime(SerifOffsetTheory):
    @classmethod
    def from_values(cls, owner=None, start_char=0, end_char=0):
        ret = cls(owner=owner)
        ret.set_offset(start_char, end_char)
        return ret
