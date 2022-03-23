from serif.theory.event import Event
from serif.theory.serif_sequence_theory import SerifSequenceTheory
from serif.xmlio import _ChildTheoryElementList
from serif.theory.enumerated_type import Genericity, Polarity, Tense, Modality

class EventSet(SerifSequenceTheory):
    _children = _ChildTheoryElementList('Event')

    @classmethod
    def from_values(cls, owner=None):
        ret = cls(owner=owner)
        return ret

    @classmethod
    def empty(cls, owner=None):
        return cls.from_values(owner=owner)

    def add_event(self, event):
        self._children.append(event)

    def add_new_event(self, event_mentions, event_type, anchor_node=None, cross_document_id=None):
        event = self.construct_event(event_mentions, event_type, anchor_node, cross_document_id=cross_document_id)
        self.add_event(event)
        return event

    def construct_event(self, event_mentions, event_type, anchor_node, cross_document_id=None):
        event = Event(owner=self)
        event.event_type = event_type
        event.event_mentions = event_mentions
        event.anchor_node = anchor_node
        event.genericity = Genericity.Specific
        event.modality = Modality.Other
        event.tense = Tense.Unspecified
        event.polarity = Polarity.Positive
        event.cross_document_instance_id = cross_document_id
        event.document.generate_id(event)
        return event
