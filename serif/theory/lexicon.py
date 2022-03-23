from serif.theory.serif_sequence_theory import SerifSequenceTheory
from serif.xmlio import _ChildTheoryElementList


class Lexicon(SerifSequenceTheory):
    _children = _ChildTheoryElementList('LexicalEntry')
