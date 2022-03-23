from serif.theory.actor_mention import ActorMention
from serif.theory.icews_event_participant_theory import ICEWSEventParticipantTheory
from serif.xmlio import _SimpleAttribute, _ReferenceAttribute


class ICEWSEventParticipant(ICEWSEventParticipantTheory):
    role = _SimpleAttribute(is_required=True)
    actor = _ReferenceAttribute('actor_id', cls=ActorMention)
