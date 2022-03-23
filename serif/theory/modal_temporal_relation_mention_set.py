from serif.theory.event_mention import EventMention
from serif.theory.mention import Mention
from serif.theory.value_mention import ValueMention

from serif.theory.modal_temporal_relation_mention import ModalTemporalRelationMention, SPECIAL_NODES
from serif.theory.modal_temporal_relation_argument import ModalTemporalRelationArgument
from serif.theory.serif_sequence_theory import SerifSequenceTheory
from serif.xmlio import _ChildTheoryElementList, _ReferenceAttribute


class ModalTemporalRelationMentionSet(SerifSequenceTheory):
    _children = _ChildTheoryElementList('ModalTemporalRelationMention')
    modal_root = _ReferenceAttribute("modal_root_id", cls=ModalTemporalRelationMention)
    temporal_root = _ReferenceAttribute("temporal_root_id", cls=ModalTemporalRelationMention)

    @classmethod
    def from_values(cls, owner=None):
        ret = cls(owner=owner)
        return ret

    @classmethod
    def empty(cls, owner=None):
        return cls.from_values(owner=owner)

    def add_modal_temporal_relation_mention(self, modal_temporal_relation_mention):
        self._children.append(modal_temporal_relation_mention)

    def construct_modal_temporal_relation_mention(
            self, relation_type, node, modal_temporal_node_type, confidence, model):

        # create rel mention object and its node wrapping the info
        mod_tmp_rel_mention = ModalTemporalRelationMention(owner=self)
        mod_tmp_rel_mention.document.generate_id(mod_tmp_rel_mention)

        mod_tmp_rel_mention_node = ModalTemporalRelationArgument(owner=mod_tmp_rel_mention)

        # set node's info
        mod_tmp_rel_mention_node.relation_type = relation_type

        if isinstance(node, Mention):
            mod_tmp_rel_mention_node.mention = node
        elif isinstance(node, ValueMention):
            mod_tmp_rel_mention_node.value_mention = node
        elif isinstance(node, EventMention):
            mod_tmp_rel_mention_node.event_mention = node
        elif isinstance(node, str):
            assert node in SPECIAL_NODES
            mod_tmp_rel_mention_node.special_node = node
        else:
            raise ValueError

        mod_tmp_rel_mention_node.modal_temporal_node_type = modal_temporal_node_type
        mod_tmp_rel_mention_node.confidence = confidence
        mod_tmp_rel_mention_node.model = model

        # set node as attribute of rel mention object
        mod_tmp_rel_mention.node = mod_tmp_rel_mention_node

        mod_tmp_rel_mention_node.document.generate_id(mod_tmp_rel_mention_node)

        return mod_tmp_rel_mention

    def add_new_modal_temporal_relation_mention(
            self, relation_type, node, modal_temporal_node_type, confidence, model):
        modal_temporal_rel_mention = self.construct_modal_temporal_relation_mention(
            relation_type, node, modal_temporal_node_type, confidence, model)
        self.add_modal_temporal_relation_mention(modal_temporal_rel_mention)
        return modal_temporal_rel_mention

    def set_modal_root(self, modal_temporal_relation_mention):
        self.modal_root = modal_temporal_relation_mention

    def set_temporal_root(self, modal_temporal_relation_mention):
        self.temporal_root = modal_temporal_relation_mention

