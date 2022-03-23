from serif.theory.serif_sequence_theory import SerifSequenceTheory
from serif.xmlio import _ChildTheoryElementList


class Metadata(SerifSequenceTheory):
    _children = _ChildTheoryElementList('Span')

    def add_span(self, span):
        self._children.append(span)
