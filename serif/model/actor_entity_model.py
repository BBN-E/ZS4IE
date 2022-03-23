from abc import abstractmethod
from serif.model.document_model import DocumentModel


class ActorEntityModel(DocumentModel):
    def __init__(self, **kwargs):
        super(ActorEntityModel, self).__init__(**kwargs)

    @abstractmethod
    def add_actor_entities_to_document(self, serif_doc):
        """
        :type serif_doc: Document
        :return: List where each element corresponds to newly added actor entity.
        :rtype: list(ActorEntity)
        """
        pass

    @staticmethod
    def add_new_actor_entity(actor_entity_set, entity, actor_uid, actor_mentions, confidence, actor_name, *,
                             name=None, actor_db_name=None, source_note=None):
        new_actor_entity = actor_entity_set.add_new_actor_entity(
            entity, actor_uid, actor_mentions, confidence, actor_name)
        new_actor_entity.name = name
        new_actor_entity.actor_db_name = actor_db_name
        new_actor_entity.source_note = source_note
        return [new_actor_entity]

    def process_document(self, serif_doc):
        if serif_doc.actor_entity_set is None:
            actor_entity_set = serif_doc.add_new_actor_entity_set()
            ''':type: ActorEntitySet'''
        self.add_actor_entities_to_document(serif_doc)
