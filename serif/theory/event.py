from serif.theory.enumerated_type import Genericity, Polarity, Tense, Modality
from serif.theory.event_mention import EventMention
from serif.theory.event_anchor import EventAnchor
from serif.theory.entity import Entity
from serif.theory.value import Value
from serif.theory.event_arg import EventArg
from serif.theory.serif_theory import SerifTheory
from serif.theory.syn_node import SynNode
from serif.theory.mention import Mention
from serif.xmlio import _ChildTheoryElementList, _SimpleAttribute, _ReferenceListAttribute, _ReferenceAttribute


class Event(SerifTheory):
    arguments = _ChildTheoryElementList('EventArg')
    event_type = _SimpleAttribute(is_required=True)
    event_mentions = _ReferenceListAttribute('event_mention_ids',
                                             cls=EventMention)
    anchors = _ChildTheoryElementList('EventAnchor')
    genericity = _SimpleAttribute(Genericity, is_required=True)
    polarity = _SimpleAttribute(Polarity, is_required=True)
    tense = _SimpleAttribute(Tense, is_required=True)
    modality = _SimpleAttribute(Modality, is_required=True)
    completion = _SimpleAttribute()
    coordinated = _SimpleAttribute(bool)
    over_time = _SimpleAttribute(bool)
    granular_template_type_attribute = _SimpleAttribute()
    annotation_id = _SimpleAttribute()
    cross_document_instance_id = _SimpleAttribute()  # ECB+

    def add_new_argument(self, role, argument_object, score):
        event_arg = self.construct_event_argument(role, argument_object, score)
        self.add_event_argument(event_arg)
        return event_arg

    def add_event_argument(self, event_arg):
        self.arguments.append(event_arg)

    def add_new_event_anchor(self, anchor, anchor_prop=None):
        anchor = self.construct_event_anchor(anchor, anchor_prop)
        self.add_event_anchor(anchor)
        return anchor
        
    def add_event_anchor(self, anchor):
        self.anchors.append(anchor)

    def construct_event_anchor(self, anchor_object, anchor_prop):
        anchor = EventAnchor(owner=self)
        anchor.anchor_prop = anchor_prop

        if isinstance(anchor_object, SynNode):
            anchor.anchor_node = anchor_object
        elif isinstance(anchor_object, EventMention):
            anchor.anchor_event_mention = anchor_object
        else:
            raise ValueError
        return anchor

    def construct_event_argument(self, role, argument_object, score):
        event_arg = EventArg(owner=self)
        event_arg.role = role
        event_arg.score = score
        if isinstance(argument_object, Entity):
            event_arg.entity = argument_object
        elif isinstance(argument_object, Value):
            event_arg.value_entity = argument_object
        elif isinstance(argument_object, EventMention):
            event_arg.event_mention = argument_object
        elif isinstance(argument_object, Mention):
            event_arg.mention = argument_object
        else:
            raise ValueError
        event_arg.document.generate_id(event_arg)
        return event_arg
