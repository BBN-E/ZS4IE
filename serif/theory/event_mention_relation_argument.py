from serif.theory.event_mention import EventMention
from serif.theory.relation_argument import RelationArgument
from serif.xmlio import _ReferenceAttribute


class EventMentionRelationArgument(RelationArgument):
    event_mention = _ReferenceAttribute('event_mention_id',
                                        cls=EventMention)
