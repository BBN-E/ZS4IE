from serif.theory.serif_syn_node_theory import SerifSynNodeTheory
from serif.theory.token import Token
from serif.xmlio import _SimpleAttribute, _ReferenceAttribute, _ChildTheoryElementList


class SynNode(SerifSynNodeTheory):
    tag = _SimpleAttribute(is_required=True)
    start_token = _ReferenceAttribute('start_token', cls=Token,
                                      is_required=True)
    end_token = _ReferenceAttribute('end_token', cls=Token,
                                    is_required=True)
    is_head = _SimpleAttribute(bool, default=False)
    _children = _ChildTheoryElementList('SynNode')
