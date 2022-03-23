from serif.theory.enumerated_type import Genericity, Polarity, Tense, Modality, DirectionOfChange
from serif.theory.event_mention_anchor import EventMentionAnchor
from serif.theory.event_mention_factor_type import EventMentionFactorType
from serif.theory.event_mention_type import EventMentionType
from serif.theory.mention import Mention
from serif.theory.proposition import Proposition
from serif.theory.serif_event_mention_theory import SerifEventMentionTheory
from serif.theory.syn_node import SynNode
from serif.theory.value_mention import ValueMention
from serif.xmlio import _SimpleAttribute, _ChildTheoryElementList, _ReferenceAttribute


class EventMention(SerifEventMentionTheory):
    arguments = _ChildTheoryElementList('EventMentionArg')
    score = _SimpleAttribute(float, default=1.0)
    event_type = _SimpleAttribute(is_required=True)
    pattern_id = _SimpleAttribute(is_required=False)
    semantic_phrase_start = _SimpleAttribute(int, is_required=False)
    semantic_phrase_end = _SimpleAttribute(int, is_required=False)
    head_start = _SimpleAttribute(int, is_required=False)   # index of start token of anchor head
    head_end = _SimpleAttribute(int, is_required=False)     # index of end token of anchor head
    genericity = _SimpleAttribute(Genericity, is_required=True)
    polarity = _SimpleAttribute(Polarity, is_required=True)
    direction_of_change = _SimpleAttribute(DirectionOfChange, is_required=False)
    tense = _SimpleAttribute(Tense, is_required=True)
    modality = _SimpleAttribute(Modality, is_required=True)
    state_of_affairs = _SimpleAttribute(bool)
    anchor_prop = _ReferenceAttribute('anchor_prop_id',
                                      cls=Proposition)
    anchor_node = _ReferenceAttribute('anchor_node_id',
                                      cls=SynNode)
    model = _SimpleAttribute(is_required=False)
    genericityScore = _SimpleAttribute(float, is_required=False)
    modalityScore = _SimpleAttribute(float, is_required=False)
    event_types = _ChildTheoryElementList('EventMentionType')
    factor_types = _ChildTheoryElementList('EventMentionFactorType')
    anchors = _ChildTheoryElementList('EventMentionAnchor')
    cluster_id = _SimpleAttribute(int, is_required=False)

    completion = _SimpleAttribute()
    coordinated = _SimpleAttribute(bool)
    over_time = _SimpleAttribute(bool)
    granular_template_type_attribute = _SimpleAttribute()

    claim_role = _SimpleAttribute()
    claim_label = _SimpleAttribute()

    def add_event_mention_anchor(self, em_anchor):
        self.anchors.append(em_anchor)

    def add_new_event_mention_anchor(self, anchor_node, anchor_prop=None):
        em_anchor = self.construct_event_mention_anchor(anchor_node, anchor_prop)
        self.add_event_mention_anchor(em_anchor)
        return em_anchor

    def construct_event_mention_anchor(self, anchor_node, anchor_prop):
        em_anchor = EventMentionAnchor(owner=self)
        em_anchor.anchor_node = anchor_node
        em_anchor.anchor_prop = anchor_prop
        return em_anchor

    def add_new_mention_argument(self, role, mention, score):
        event_mention_arg = self.construct_event_mention_argument(role, mention, score)
        self.add_event_mention_argument(event_mention_arg)
        return event_mention_arg

    def add_new_value_mention_argument(self, role, value_mention, score):
        event_mention_arg = self.construct_event_mention_argument(
            role, value_mention, score)
        self.add_event_mention_argument(event_mention_arg)
        return event_mention_arg

    def add_new_syn_node_argument(self, role, syn_node, score):
        event_mention_arg = self.construct_event_mention_argument(role, syn_node, score)
        self.add_event_mention_argument(event_mention_arg)
        return event_mention_arg

    def add_new_event_mention_argument(self, role, serif_em, score):
        event_mention_arg = self.construct_event_mention_argument(role, serif_em, score)
        self.add_event_mention_argument(event_mention_arg)
        return event_mention_arg

    def add_event_mention_argument(self, event_mention_argument):
        self.arguments.append(event_mention_argument)

    # argument_object could be Mention, ValueMention, SynNode, or EventMention
    def construct_event_mention_argument(self, role, argument_object, score):
        from serif.theory.event_mention_arg import EventMentionArg
        event_mention_argument = EventMentionArg(owner=self)
        event_mention_argument.role = role
        event_mention_argument.score = score
        if isinstance(argument_object, Mention):
            event_mention_argument.mention = argument_object
        elif isinstance(argument_object, ValueMention):
            event_mention_argument.value_mention = argument_object
        elif isinstance(argument_object, SynNode):
            event_mention_argument.syn_node = argument_object
        elif isinstance(argument_object, EventMention):
            event_mention_argument.event_mention = argument_object
        else:
            raise ValueError
        event_mention_argument.document.generate_id(event_mention_argument)
        return event_mention_argument

    def add_new_event_mention_type(self, em_type, score):
        event_mention_type = self.construct_event_mention_type(em_type, score)
        self.add_event_mention_type(event_mention_type)
        return event_mention_type

    def add_event_mention_type(self, event_mention_type):
        self.event_types.append(event_mention_type)

    def construct_event_mention_type(self, emf_type, score):
        event_mention_type = EventMentionType(owner=self)
        event_mention_type.event_type = emf_type
        event_mention_type.score = score
        return event_mention_type

    def add_new_event_mention_factor_type(self, emf_type, score):
        event_mention_factor_type = self.construct_event_mention_factor_type(emf_type, score)
        self.add_event_mention_factor_type(event_mention_factor_type)
        return event_mention_factor_type

    def add_event_mention_factor_type(self, event_mention_factor_type):
        self.factor_types.append(event_mention_factor_type)

    def construct_event_mention_factor_type(self, emf_type, score):
        event_mention_factor_type = EventMentionFactorType(owner=self)
        event_mention_factor_type.event_type = emf_type
        event_mention_factor_type.score = score
        return event_mention_factor_type

    def _get_summary(self):
        if self.anchor_node is None:
            return None
        else:
            return self.anchor_node._get_summary()

    @property
    def tokens(self):
        """The tokens contained in this event mention."""

        if self.semantic_phrase_start and self.semantic_phrase_end:
            sent = self.sentence
            return sent.token_sequence[self.semantic_phrase_start: self.semantic_phrase_end + 1]
        if self.anchor_node is not None:
            return self.anchor_node.tokens

    @property
    def start_token(self):
        return self.tokens[0]

    @property
    def end_token(self):
        return self.tokens[-1]

    @property
    def start_char(self):
        """The start character index of this EventMention"""

        if self.semantic_phrase_start:
            sent = self.sentence
            return sent.token_sequence[self.semantic_phrase_start].start_char

        if self.anchor_node is not None:
            return self.anchor_node.start_token.start_char


    @property
    def end_char(self):
        """The end character index of this EventMention"""

        if self.semantic_phrase_end:
            sent = self.sentence
            return sent.token_sequence[self.semantic_phrase_end].end_char

        if self.anchor_node is not None:
            return self.anchor_node.start_token.end_char


    @property
    def start_edt(self):
        if self.semantic_phrase_start:
            sent = self.sentence
            return sent.token_sequence[self.semantic_phrase_start].start_edt

        if self.anchor_node is not None:
            return self.anchor_node.start_token.start_edt


    @property
    def end_edt(self):
        """The end character index of this EventMention"""

        if self.semantic_phrase_end:
            sent = self.sentence
            return sent.token_sequence[self.semantic_phrase_end].end_edt

        if self.anchor_node is not None:
            return self.anchor_node.start_token.end_edt


    @property
    def text(self):
        """The text content of this mention."""
        if self.semantic_phrase_start and self.semantic_phrase_end:
            sent = self.sentence
            return sent.token_sequence.get_original_text_substring(self.start_char, self.end_char)

        if self.anchor_node is not None:
            return self.anchor_node.text

