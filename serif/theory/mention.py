from serif.theory.enumerated_type import MentionType
from serif.theory.serif_mention_theory import SerifMentionTheory
from serif.theory.syn_node import SynNode
from serif.theory.token import Token
from serif.xmlio import _ReferenceAttribute, _SimpleAttribute


class Mention(SerifMentionTheory):
    syn_node = _ReferenceAttribute('syn_node_id', cls=SynNode)
    start_token = _ReferenceAttribute('start_token', cls=Token)
    end_token = _ReferenceAttribute('end_token', cls=Token)
    head_start_token = _ReferenceAttribute('head_start_token', cls=Token)
    head_end_token = _ReferenceAttribute('head_end_token', cls=Token)
    mention_type = _SimpleAttribute(MentionType, is_required=True)
    entity_type = _SimpleAttribute(is_required=True)
    entity_subtype = _SimpleAttribute(default='UNDET',is_required=True)
    is_metonymy = _SimpleAttribute(bool, default=False,is_required=True)
    intended_type = _SimpleAttribute(default='UNDET')
    role_type = _SimpleAttribute(default='UNDET')
    link_confidence = _SimpleAttribute(float)
    confidence = _SimpleAttribute(float)
    parent_mention = _ReferenceAttribute('parent', cls='Mention')
    child_mention = _ReferenceAttribute('child', cls='Mention')
    next_mention = _ReferenceAttribute('next', cls='Mention')
    model = _SimpleAttribute()
    pattern = _SimpleAttribute()
    coref_chain = _SimpleAttribute()
    claim_role = _SimpleAttribute()
