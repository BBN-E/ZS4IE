from serif.theory.serif_sequence_theory import SerifSequenceTheory
from serif.theory.value import Value

from serif.xmlio import _ChildTheoryElementList


class ValueSet(SerifSequenceTheory):
    _children = _ChildTheoryElementList('Value')

    @classmethod
    def from_values(cls, owner=None, score=0):
        ret = cls(owner=owner)
        ret.score = score
        return ret

    @classmethod
    def empty(cls, owner=None):
        return cls.from_values(owner=owner)

    def add_value(self, value_mention):
        self._children.append(value_mention)
        
    def add_new_value(self, value_mention, value_type, timex_string):
        value = self.construct_value(
            value_mention, value_type, timex_string)
        self.add_value(value)
        return value

    def construct_value(self, value_mention, value_type, timex_string):
        value = Value(owner=self)
        value.value_mention = value_mention
        value.value_type = value_type
        value.timex_val = timex_string
        value.document.generate_id(value)
        return value
