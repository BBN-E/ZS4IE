from serif.theory.name import Name
from serif.theory.serif_sequence_theory import SerifSequenceTheory
from serif.theory.token_sequence import TokenSequence
from serif.xmlio import _SimpleAttribute, _ReferenceAttribute, _ChildTheoryElementList


class NameTheory(SerifSequenceTheory):
    score = _SimpleAttribute(float)
    token_sequence = _ReferenceAttribute('token_sequence_id',
                                         cls=TokenSequence)
    _children = _ChildTheoryElementList('Name')

    @classmethod
    def from_values(cls, owner=None, token_sequence=None, score=0):
        ret = cls(owner=owner)
        ret.token_sequence = token_sequence
        ret.score = score
        return ret

    @classmethod
    def empty(cls, owner=None, token_sequence=None):
        return cls.from_values(owner=owner, token_sequence=token_sequence)

    def add_name(self, name):
        self._children.append(name)

    def add_new_name(self, entity_type, start_token, end_token):
        name = self.construct_name(entity_type, start_token, end_token)
        self.add_name(name)
        return name

    def construct_name(self, entity_type, start_token, end_token):
        name = Name(owner=self)
        name.entity_type = entity_type
        name.start_token = start_token
        name.end_token = end_token
        name.document.generate_id(name)
        name.start_char = start_token.start_char
        name.end_char = end_token.end_char
        name.start_edt = start_token.start_edt
        name.end_edt = end_token.end_edt
        return name
