from serif.theory.serif_theory import SerifTheory
from serif.xmlio import _SimpleAttribute


class Attribute(SerifTheory):
    key = _SimpleAttribute(is_required=True)
    val = _SimpleAttribute(is_required=True)
