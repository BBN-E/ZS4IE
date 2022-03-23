from serif.theory.rel_mention import RelMention
from serif.theory.serif_sequence_theory import SerifSequenceTheory
from serif.xmlio import _SimpleAttribute, _ChildTheoryElementList


class RelMentionSet(SerifSequenceTheory):
    score = _SimpleAttribute(float)
    _children = _ChildTheoryElementList('RelMention')

    @classmethod
    def from_values(cls, owner=None, score=0):
        ret = cls(owner=owner)
        ret.score = score
        return ret

    @classmethod
    def empty(cls, owner=None):
        return cls.from_values(owner=owner)

    def add_relation_mention(self, rel_mention):
        self._children.append(rel_mention)

    def add_new_relation_mention(
            self, left_mention, right_mention, relation_type, tense, modality):
        relation_mention = self.construct_relation_mention(
            left_mention, right_mention, relation_type, tense, modality)
        self.add_relation_mention(relation_mention)
        return relation_mention

    def construct_relation_mention(
            self, left_mention, right_mention, relation_type, tense, modality):
        rel_mention = RelMention(owner=self)
        rel_mention.left_mention = left_mention
        rel_mention.right_mention = right_mention
        rel_mention.type = relation_type
        rel_mention.tense = tense
        rel_mention.modality = modality
        rel_mention.document.generate_id(rel_mention)
        return rel_mention
