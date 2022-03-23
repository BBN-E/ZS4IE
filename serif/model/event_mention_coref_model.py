from abc import abstractmethod
from serif.model.document_model import DocumentModel
from serif.model.validate import *
from serif.theory.enumerated_type import Genericity, Polarity, Modality, Tense


class EventMentionCoreferenceModel(DocumentModel):

    def __init__(self, **kwargs):
        super(EventMentionCoreferenceModel, self).__init__(**kwargs)

    @abstractmethod
    def add_new_events_to_document(self, serif_doc):
        """
        :type serif_doc: Document
        :return: List where each element corresponds to one Event.
        :rtype: list(Event)
        """
        pass

    @staticmethod
    def add_new_event(event_set, event_mentions, *, event_type=None, anchor_node=None, genericity=Genericity.Specific,
                      modality=Modality.Other, tense=Tense.Unspecified, polarity=Polarity.Positive, completion=None,
                      coordinated=None, over_time=None, granular_template_type_attribute=None, annotation_id=None,
                      cross_document_instance_id=None):
        if event_type is None:
            event_type = 'UNDET'
            event_types = set()
            for mention in event_mentions:
                event_types.add(mention.event_type)
                event_types.update(i.event_type for i in mention.event_types)
                event_types.update(i.event_type for i in mention.factor_types)
            if len(event_types) == 1:
                event_type = list(event_types)[0]
        event = event_set.add_new_event(event_mentions, event_type, anchor_node)
        event.genericity = genericity
        event.modality = modality
        event.tense = tense
        event.polarity = polarity
        event.completion = completion
        event.coordinated = coordinated
        event.over_time = over_time
        event.granular_template_type_attribute = granular_template_type_attribute
        event.annotation_id = annotation_id
        event.cross_document_instance_id = cross_document_instance_id
        return [event]

    def process_document(self, serif_doc):
        validate_doc_sentences(serif_doc)
        if serif_doc.event_set is None:
            event_set = serif_doc.add_new_event_set()
        self.add_new_events_to_document(serif_doc)
