from serif.theory.actor_entity import ActorEntity
from serif.theory.serif_sequence_theory import SerifSequenceTheory
from serif.xmlio import _ChildTheoryElementList


class ActorEntitySet(SerifSequenceTheory):
    _children = _ChildTheoryElementList('ActorEntity')

    @classmethod
    def from_values(cls, owner=None):
        ret = cls(owner=owner)
        return ret

    @classmethod
    def empty(cls, owner=None):
        return cls.from_values(owner=owner)

    def add_actor_entity(self, actor_entity):
        self._children.append(actor_entity)

    def add_new_actor_entity(
            self, entity, actor_uid, actor_mentions, confidence, actor_name):
        actor_entity = self.construct_actor_entity(
            entity, actor_uid, actor_mentions, confidence, actor_name)
        self.add_actor_entity(actor_entity)
        return actor_entity

    def construct_actor_entity(
            self, entity, actor_uid, actor_mentions, confidence, actor_name):
        actor_entity = ActorEntity(owner=self)
        actor_entity.entity = entity
        actor_entity.actor_uid = actor_uid
        actor_entity.actor_mentions = actor_mentions
        actor_entity.confidence = confidence
        actor_entity.actor_name = actor_name
        actor_entity.document.generate_id(actor_entity)
        return actor_entity
