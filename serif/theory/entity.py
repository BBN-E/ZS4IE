from serif.theory.mention import Mention
from serif.theory.serif_entity_theory import SerifEntityTheory
from serif.xmlio import _SimpleAttribute, _ReferenceListAttribute


class Entity(SerifEntityTheory):
    mentions = _ReferenceListAttribute('mention_ids', cls=Mention)
    entity_type = _SimpleAttribute(is_required=True)
    entity_subtype = _SimpleAttribute(default='UNDET')
    is_generic = _SimpleAttribute(bool, is_required=True)
    canonical_name = _SimpleAttribute()
    entity_guid = _SimpleAttribute()
    confidence = _SimpleAttribute(float, default=1.0)
    mention_confidences = _SimpleAttribute()
    cross_document_instance_id = _SimpleAttribute()  # ECB+
    model = _SimpleAttribute()