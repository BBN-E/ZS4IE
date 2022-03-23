from serif.theory.serif_sequence_theory import SerifSequenceTheory
from serif.xmlio import _ChildTheoryElementList


class FactSet(SerifSequenceTheory):
    _children = _ChildTheoryElementList('Fact')
