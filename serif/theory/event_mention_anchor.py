from serif.theory.proposition import Proposition
from serif.theory.serif_theory import SerifTheory
from serif.theory.syn_node import SynNode
from serif.xmlio import _SimpleAttribute, _ReferenceAttribute


class EventMentionAnchor(SerifTheory):
    anchor_prop = _ReferenceAttribute('anchor_prop_id',
                                      cls=Proposition)
    anchor_node = _ReferenceAttribute('anchor_node_id',
                                      cls=SynNode)
    semantic_phrase_start = _SimpleAttribute()
    semantic_phrase_end = _SimpleAttribute()
    head_start = _SimpleAttribute(int, is_required=False)   # index of start token of anchor head
    head_end = _SimpleAttribute(int, is_required=False)     # index of end token of anchor head
