from serif.theory.mention import Mention
from serif.theory.serif_theory import SerifTheory
from serif.theory.value_mention import ValueMention
from serif.theory.event_mention import EventMention
from serif.xmlio import _SimpleAttribute, _ReferenceAttribute
from serif.theory.enumerated_type import Polarity


class ModalTemporalRelationArgument(SerifTheory):

    relation_type = _SimpleAttribute()
    polarity = _SimpleAttribute(Polarity)

    is_aida_claim = _SimpleAttribute(bool)

    # different modal/temporal node types
    mention = _ReferenceAttribute('mention_id', cls=Mention)
    value_mention = _ReferenceAttribute('value_mention_id', cls=ValueMention)
    event_mention = _ReferenceAttribute('event_mention_id', cls=EventMention)
    special_node = _SimpleAttribute(str)  # ROOT_NODE, AUTHOR_NODE, NULL_CONCEIVER_NODE

    modal_temporal_node_type = _SimpleAttribute(str)  # "Conceiver", "Event-VBD", "Timex" etc.

    model = _SimpleAttribute()
    confidence = _SimpleAttribute(float)
    value = property(
        lambda self: self.special_node or self.mention or self.value_mention or self.event_mention)
