from serif.theory.serif_sequence_theory import SerifSequenceTheory
from serif.theory.value_mention import ValueMention
from serif.theory.token_sequence import TokenSequence
from serif.xmlio import _SimpleAttribute, _ReferenceAttribute, _ChildTheoryElementList


class ValueMentionSet(SerifSequenceTheory):
    score = _SimpleAttribute(float)
    token_sequence = _ReferenceAttribute('token_sequence_id',
                                         cls=TokenSequence)
    _children = _ChildTheoryElementList('ValueMention')

    @classmethod
    def from_values(cls, owner=None, token_sequence=None, score=0.0):
        ret = cls(owner=owner)
        ret.token_sequence = token_sequence
        ret.score = score
        return ret

    @classmethod
    def empty(cls, owner=None, token_sequence=None):
        return cls.from_values(owner=owner, token_sequence=token_sequence)

    def add_value_mention(self, value_mention):
        self._children.append(value_mention)

    def add_new_value_mention(self, start_token, end_token, value_type):
        value_mention = self.construct_value_mention(start_token, end_token, value_type)
        self.add_value_mention(value_mention)
        return value_mention

    def construct_value_mention(self, start_token, end_token, value_type):
        value_mention = ValueMention(owner=self)
        value_mention.start_token = start_token
        value_mention.end_token = end_token
        value_mention.start_char = start_token.start_char
        value_mention.end_char = end_token.end_char
        value_mention.start_edt = start_token.start_edt
        value_mention.end_edt = end_token.end_edt
        value_mention.value_type = value_type
        value_mention.document.generate_id(value_mention)
        return value_mention
