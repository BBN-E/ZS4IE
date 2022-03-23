from serif.theory.serif_sequence_theory import SerifSequenceTheory
from serif.xmlio import _ChildTheoryElementList, _ChildTextElement


class Entry(SerifSequenceTheory):
    _children = _ChildTheoryElementList('Attribute')
    contents = _ChildTextElement('Contents')
