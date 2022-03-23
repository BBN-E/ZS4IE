from serif.theory.serif_theory import SerifTheory
from serif.xmlio import _SimpleAttribute


class Timex2(SerifTheory):
    val = _SimpleAttribute(is_required=True)
    mod = _SimpleAttribute()
    set = _SimpleAttribute(bool)
    granularity = _SimpleAttribute()
    periodicity = _SimpleAttribute()
    anchor_val = _SimpleAttribute()
    anchor_dir = _SimpleAttribute()
    non_specific = _SimpleAttribute(bool)
