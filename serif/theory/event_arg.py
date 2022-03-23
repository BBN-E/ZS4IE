from serif.xmlio import _SimpleAttribute, _ReferenceAttribute, _ReferenceListAttribute
from serif.theory.serif_theory import SerifTheory
from serif.theory.entity import Entity
from serif.theory.value import Value
from serif.theory.event_mention import EventMention
from serif.theory.mention import Mention

class EventArg(SerifTheory):
    role = _SimpleAttribute(default='')
    entity = _ReferenceAttribute('entity_id',
                                 cls=Entity)
    value_entity = _ReferenceAttribute('value_id',
                                       cls=Value)
    event_mention = _ReferenceAttribute('event_mention_id',
                                        cls=EventMention)
    mention = _ReferenceAttribute('mention_id',
                                  cls=Mention)
    time_attachments = _ReferenceListAttribute('time_attachment_ids',
                                              cls=Entity)
    irrealis = _SimpleAttribute()
    score = _SimpleAttribute(float, default=0.0)
    value = property(
        lambda self: self.entity or self.value_entity or self.event_mention)
