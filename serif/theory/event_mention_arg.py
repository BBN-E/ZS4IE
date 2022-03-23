from serif.theory.mention import Mention
from serif.theory.serif_offset_theory import SerifOffsetTheory
from serif.theory.syn_node import SynNode
from serif.theory.value_mention import ValueMention
from serif.xmlio import _SimpleAttribute, _ReferenceAttribute


class EventMentionArg(SerifOffsetTheory):
    role = _SimpleAttribute(default='')
    mention = _ReferenceAttribute('mention_id',
                                  cls=Mention)
    value_mention = _ReferenceAttribute('value_mention_id',
                                        cls=ValueMention)
    syn_node = _ReferenceAttribute('syn_node_id',
                                   cls=SynNode)
    event_mention = _ReferenceAttribute('event_mention_id',
                                        cls='EventMention')
    score = _SimpleAttribute(float, is_required=True)
    model = _SimpleAttribute(is_required=False)
    pattern = _SimpleAttribute(is_required=False)
    value = property(
        lambda self: self.mention or self.value_mention or self.syn_node or self.event_mention)
