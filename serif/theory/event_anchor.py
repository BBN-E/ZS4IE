from serif.theory.proposition import Proposition
from serif.theory.serif_theory import SerifTheory
from serif.theory.syn_node import SynNode
from serif.theory.event_mention import EventMention
from serif.xmlio import _ReferenceAttribute


class EventAnchor(SerifTheory):
    anchor_prop = _ReferenceAttribute('anchor_prop_id',
                                      cls=Proposition)
    anchor_node = _ReferenceAttribute('anchor_node_id',
                                      cls=SynNode)
    anchor_event_mention = _ReferenceAttribute('anchor_event_mention_id',
                                               cls=EventMention)
