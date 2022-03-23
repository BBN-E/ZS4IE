from serif.theory.serif_theory import SerifTheory
from serif.xmlio import _ChildTheoryElementList, _SimpleAttribute


class Field(SerifTheory):
    name = _SimpleAttribute(is_required=True)
    entries = _ChildTheoryElementList('Entry')
