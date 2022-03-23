from abc import abstractmethod
from serif.model.document_model import DocumentModel
from serif.model.validate import *
from serif.theory.enumerated_type import Tense, Modality


class RelationModel(DocumentModel):

    def __init__(self, **kwargs):
        super(RelationModel, self).__init__(**kwargs)

    @abstractmethod
    def add_relations_to_document(self, serif_doc):
        pass

    @staticmethod
    def add_new_relation(relation_set, relation_type, left_entity, right_entity, relation_mentions, *,
                         tense=Tense.Unspecified, modality=Modality.Asserted, confidence=1.0, model=None,
                         pattern=None):
        relations = []
        relation = relation_set.add_new_relation(
            relation_mentions, relation_type, left_entity, right_entity)
        relations.append(relation)
        for relation in relations:
            relation.tense = tense
            relation.modality = modality
            relation.confidence = confidence
            relation.model = model
            relation.pattern = pattern
        return relations

    def process_document(self, serif_doc):
        validate_doc_entity_sets(serif_doc)
        relation_set = serif_doc.relation_set
        if relation_set is None:
            relation_set = serif_doc.add_new_relation_set()
            ''':type: RelationSet'''
        self.add_relations_to_document(serif_doc)
