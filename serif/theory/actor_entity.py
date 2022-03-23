from serif.theory.actor_mention import ActorMention
from serif.theory.entity import Entity
from serif.theory.serif_theory import SerifTheory
from serif.xmlio import _ReferenceAttribute, _SimpleAttribute, _ReferenceListAttribute, _TextOfElement


class ActorEntity(SerifTheory):
    entity = _ReferenceAttribute('entity_id', cls=Entity, is_required=True)
    actor_uid = _SimpleAttribute(int)
    actor_mentions = _ReferenceListAttribute('actor_mention_ids', cls=ActorMention)
    confidence = _SimpleAttribute(float, is_required=True, default=0.0)
    name = _TextOfElement(strip=True)
    actor_name = _SimpleAttribute()
    actor_db_name = _SimpleAttribute()
    source_note = _SimpleAttribute()
    actor_type = _SimpleAttribute()
    actor_affiliation = _SimpleAttribute()