from serif.theory.serif_theory import SerifTheory
from serif.xmlio import _SimpleAttribute


class AlternatePOS(SerifTheory):
    tag = _SimpleAttribute(is_required=True)
    prob = _SimpleAttribute(float)
