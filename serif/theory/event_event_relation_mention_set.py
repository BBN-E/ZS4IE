from serif.theory.event_event_relation_mention import EventEventRelationMention
from serif.theory.serif_sequence_theory import SerifSequenceTheory
from serif.xmlio import _ChildTheoryElementList


class EventEventRelationMentionSet(SerifSequenceTheory):
    _children = _ChildTheoryElementList('EventEventRelationMention')

    @classmethod
    def from_values(cls, owner=None):
        ret = cls(owner=owner)
        return ret

    @classmethod
    def empty(cls, owner=None):
        return cls.from_values(owner=owner)

    def add_event_event_relation_mention(self, event_event_relation_mention):
        self._children.append(event_event_relation_mention)

    def construct_event_event_relation_mention(
            self, relation_type, confidence, model_name):
        evt_evt_rel_mention = EventEventRelationMention(owner=self)
        evt_evt_rel_mention.relation_type = relation_type
        evt_evt_rel_mention.confidence = confidence
        evt_evt_rel_mention.model = model_name
        evt_evt_rel_mention.document.generate_id(evt_evt_rel_mention)
        return evt_evt_rel_mention

    def add_new_event_event_relation_mention(
            self, relation_type, confidence, model_name):
        event_event_rel_mention = self.construct_event_event_relation_mention(
            relation_type, confidence, model_name)
        self.add_event_event_relation_mention(event_event_rel_mention)
        return event_event_rel_mention
