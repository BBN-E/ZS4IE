from serif.theory.mention import Mention
from serif.theory.serif_theory import SerifTheory
from serif.theory.syn_node import SynNode
from serif.theory.value_mention import ValueMention
from serif.xmlio import _SimpleAttribute, _ReferenceAttribute, _ChildTheoryElement


class FlexibleEventMentionArg(SerifTheory):
    role = _SimpleAttribute(is_required=True)
    start_sentence = _SimpleAttribute(int, is_required=False)
    end_sentence = _SimpleAttribute(int, is_required=False)
    start_token = _SimpleAttribute(int, is_required=False)
    end_token = _SimpleAttribute(int, is_required=False)
    mention = _ReferenceAttribute('mention_id', cls=Mention, is_required=False)
    syn_node = _ReferenceAttribute('syn_node_id', cls=SynNode, is_required=False)
    value_mention = _ReferenceAttribute('value_mention_id', cls=ValueMention, is_required=False)
    geo_uid = _SimpleAttribute()
    geo_country = _SimpleAttribute()
    temporal_resolution = _ChildTheoryElement('Timex2')
