from serif.theory.entity import Entity
from serif.theory.serif_sequence_theory import SerifSequenceTheory
from serif.xmlio import _SimpleAttribute, _ChildTheoryElementList


class EntitySet(SerifSequenceTheory):
    score = _SimpleAttribute(float)
    _children = _ChildTheoryElementList('Entity')

    @classmethod
    def from_values(cls, owner=None, score=0):
        ret = cls(owner=owner)
        ret.score = score
        return ret

    @classmethod
    def empty(cls, owner=None):
        return cls.from_values(owner=owner)

    def add_entity(self, entity):
        self._children.append(entity)

    def add_new_entity(self, mentions, entity_type, entity_subtype, is_generic):
        entity = self.construct_entity(mentions, entity_type, entity_subtype, is_generic)
        self.add_entity(entity)
        return entity

    def construct_entity(self, mentions, entity_type, entity_subtype, is_generic):
        entity = Entity(owner=self)
        entity.entity_type = entity_type
        if entity_subtype is not None:
            entity.entity_subtype = entity_subtype
        for mention in mentions:
            entity.mentions.append(mention)
        entity.is_generic = is_generic
        entity.document.generate_id(entity)
        return entity
