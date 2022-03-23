from serif.theory.serif_theory import SerifTheory
from serif.xmlio import _ChildTheoryElementList


class Segment(SerifTheory):
    attributes = _ChildTheoryElementList('Attribute')
    fields = _ChildTheoryElementList('Field')
