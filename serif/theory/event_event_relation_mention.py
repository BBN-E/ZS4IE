from serif.theory.event_mention_relation_argument import EventMentionRelationArgument
from serif.theory.icews_event_mention_relation_argument import ICEWSEventMentionRelationArgument
from serif.theory.serif_theory import SerifTheory
from serif.xmlio import _SimpleAttribute, _ChildTheoryElementList
from serif.theory.enumerated_type import Polarity

class EventEventRelationMention(SerifTheory):
    pattern = _SimpleAttribute()
    relation_type = _SimpleAttribute()
    confidence = _SimpleAttribute(float)
    model = _SimpleAttribute()

    event_mention_relation_arguments = _ChildTheoryElementList('EventMentionRelationArgument')
    icews_event_mention_relation_arguments = _ChildTheoryElementList('ICEWSEventMentionRelationArgument')
    polarity = _SimpleAttribute(Polarity)
    trigger_text = _SimpleAttribute()

    def add_new_event_mention_argument(self, role, event_mention):
        event_mention_rel_arg = self.construct_event_mention_relation_argument(role, event_mention)
        self.add_event_mention_relation_argument(event_mention_rel_arg)
        return event_mention_rel_arg

    def add_new_icews_event_mention_argument(self, role, icews_event_mention):
        icews_event_mention_rel_arg = self.construct_icews_event_mention_relation_argument(role, icews_event_mention)
        self.add_icews_event_mention_relation_argument(icews_event_mention_rel_arg)
        return icews_event_mention_rel_arg

    def construct_event_mention_relation_argument(self, role, event_mention):
        evt_mention_rel_argument = EventMentionRelationArgument(owner=self)
        evt_mention_rel_argument.role = role
        evt_mention_rel_argument.event_mention = event_mention
        evt_mention_rel_argument.document.generate_id(evt_mention_rel_argument)
        return evt_mention_rel_argument

    def construct_icews_event_mention_relation_argument(self, role, icews_event_mention):
        evt_mention_rel_argument = ICEWSEventMentionRelationArgument(owner=self)
        evt_mention_rel_argument.role = role
        evt_mention_rel_argument.icews_event_mention = icews_event_mention
        evt_mention_rel_argument.document.generate_id(evt_mention_rel_argument)
        return evt_mention_rel_argument

    def add_event_mention_relation_argument(self, evt_mention_rel_argument):
        self.event_mention_relation_arguments.append(evt_mention_rel_argument)

    def add_icews_event_mention_relation_argument(self, evt_mention_rel_argument):
        self.icews_event_mention_relation_arguments.append(evt_mention_rel_argument)
