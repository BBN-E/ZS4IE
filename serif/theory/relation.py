from serif.theory.entity import Entity
from serif.theory.enumerated_type import Tense, Modality
from serif.theory.rel_mention import RelMention
from serif.theory.serif_theory import SerifTheory
from serif.xmlio import _ReferenceAttribute, _ReferenceListAttribute, _SimpleAttribute


class Relation(SerifTheory):
    rel_mentions = _ReferenceListAttribute('rel_mention_ids',
                                           cls=RelMention)
    relation_type = _SimpleAttribute(is_required=True, attr_name='type')
    left_entity = _ReferenceAttribute('left_entity_id', cls=Entity,
                                      is_required=True)
    right_entity = _ReferenceAttribute('right_entity_id', cls=Entity,
                                       is_required=True)
    tense = _SimpleAttribute(Tense, is_required=True)
    modality = _SimpleAttribute(Modality, is_required=True)
    confidence = _SimpleAttribute(float, default=1.0,is_required=True)
    model = _SimpleAttribute()
    pattern = _SimpleAttribute()