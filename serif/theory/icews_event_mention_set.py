from serif.theory.serif_sequence_theory import SerifSequenceTheory
from serif.xmlio import _ChildTheoryElementList


class ICEWSEventMentionSet(SerifSequenceTheory):
    _children = _ChildTheoryElementList('ICEWSEventMention')
