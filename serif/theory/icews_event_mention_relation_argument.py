from serif.theory.icews_event_mention import ICEWSEventMention
from serif.theory.relation_argument import RelationArgument
from serif.xmlio import _ReferenceAttribute


class ICEWSEventMentionRelationArgument(RelationArgument):
    icews_event_mention = _ReferenceAttribute('icews_event_mention_id',
                                              cls=ICEWSEventMention)
