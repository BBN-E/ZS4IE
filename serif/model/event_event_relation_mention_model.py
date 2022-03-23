from abc import abstractmethod

from serif.model.document_model import DocumentModel
from serifxml3 import EventMention, ICEWSEventMention


class EventEventRelationMentionModel(DocumentModel):

    def __init__(self, **kwargs):
        super(EventEventRelationMentionModel, self).__init__(**kwargs)

    @abstractmethod
    def add_event_event_relation_mentions_to_document(self, serif_doc):
        pass

    @staticmethod
    def add_new_event_event_relation_mention(eerm_set, relation_type, confidence, model_name,
                                             arg1_event_mention, arg2_event_mention, *, pattern=None,
                                             polarity=None, trigger_text=None):
        event_event_relation_mentions = []
        # construct object
        eerm = eerm_set.add_new_event_event_relation_mention(
            relation_type, confidence, model_name)

        if isinstance(arg1_event_mention, EventMention):
            eerm.add_new_event_mention_argument("arg1", arg1_event_mention)
        elif isinstance(arg1_event_mention, ICEWSEventMention):
            eerm.add_new_icews_event_mention_argument("arg1", arg1_event_mention)
        else:
            raise TypeError("Cannot support {}".format(type(arg1_event_mention)))

        if isinstance(arg2_event_mention, EventMention):
            eerm.add_new_event_mention_argument("arg2", arg2_event_mention)
        elif isinstance(arg2_event_mention, ICEWSEventMention):
            eerm.add_new_icews_event_mention_argument("arg2", arg2_event_mention)
        else:
            raise TypeError("Cannot support {}".format(type(arg2_event_mention)))

        eerm.pattern = pattern
        eerm.polarity = polarity
        eerm.trigger_text = trigger_text
        event_event_relation_mentions.append(eerm)
        return event_event_relation_mentions

    def process_document(self, serif_doc):
        eerm_set = serif_doc.event_event_relation_mention_set
        if eerm_set is None:
            eerm_set = \
                serif_doc.add_new_event_event_relation_mention_set()
            ''':type: EventEventRelationMentionSet'''
        self.add_event_event_relation_mentions_to_document(serif_doc)
