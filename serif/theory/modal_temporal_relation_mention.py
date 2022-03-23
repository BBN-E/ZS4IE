from serif.theory.event_mention import EventMention
from serif.theory.mention import Mention
from serif.theory.value_mention import ValueMention

from serif.theory.modal_temporal_relation_argument import ModalTemporalRelationArgument

from serif.theory.serif_theory import SerifTheory
from serif.xmlio import _SimpleAttribute, _ReferenceAttribute, _ChildTheoryElement, _ChildTheoryElementList, _ReferenceListAttribute
from serif.theory.enumerated_type import Polarity

ROOT_NODE = "ROOT_NODE"
AUTHOR_NODE = "AUTHOR_NODE"
NULL_CONCEIVER_NODE = "NULL_CONCEIVER_NODE"
DCT_NODE = "DCT_NODE"
SPECIAL_NODES = {ROOT_NODE, AUTHOR_NODE, NULL_CONCEIVER_NODE, DCT_NODE}

class ModalTemporalRelationMention(SerifTheory):

    # node = _ReferenceAttribute('modal_temporal_relation_argument_id', cls=ModalTemporalRelationArgument)  # wrapper for mtdp node attributes
    node = _ChildTheoryElement('ModalTemporalRelationArgument')  # wrapper for mtdp node attributes
    children = _ReferenceListAttribute('modal_temporal_relation_mention_child_ids')

    def add_child(self, relation_type, node, modal_temporal_node_type, confidence=1.0, model='mtdp'):

        child = ModalTemporalRelationMention(owner=self.owner)
        child.document.generate_id(child)

        child_node = ModalTemporalRelationArgument(owner=child)

        child_node.relation_type = relation_type

        if isinstance(node, Mention):
            child_node.mention = node
        elif isinstance(node, ValueMention):
            child_node.value_mention = node
        elif isinstance(node, EventMention):
            child_node.event_mention = node
        elif isinstance(node, str):
            assert node in SPECIAL_NODES
            child_node.special_node = node
        else:
            raise ValueError

        child_node.modal_temporal_node_type = modal_temporal_node_type
        child_node.model = model
        child_node.confidence = confidence

        child.node = child_node

        child_node.document.generate_id(child_node)

        self.children.append(child)  # add to children
        self.owner.add_modal_temporal_relation_mention(child)  # add to document's rel mention set
        return child
