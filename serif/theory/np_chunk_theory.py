from serif.theory.serif_sequence_theory import SerifSequenceTheory
from serif.theory.token_sequence import TokenSequence
from serif.xmlio import _ReferenceAttribute, _ChildTheoryElementList, _ChildTheoryElement, _SimpleAttribute


class NPChunkTheory(SerifSequenceTheory):
    score = _SimpleAttribute(float)
    token_sequence = _ReferenceAttribute('token_sequence_id',
                                         cls=TokenSequence)
    _children = _ChildTheoryElementList('NPChunk')
    _parse = _ChildTheoryElement('Parse')
