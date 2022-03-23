from serif.theory.serif_sequence_theory import SerifSequenceTheory
from serif.xmlio import _ChildTheoryElementList


class Sentences(SerifSequenceTheory):
    _children = _ChildTheoryElementList('Sentence', index_attrib='sent_no')

    @classmethod
    def from_values(cls, owner=None):
        ret = cls(owner=owner)
        return ret

    @classmethod
    def empty(cls, owner=None):
        return cls.from_values(owner=owner)

    def add_sentence(self, sentence):
        self._children.append(sentence)

    def add_new_sentence(self, start_char, end_char, region):
        sentence = self.construct_sentence(start_char, end_char, region)
        self.add_sentence(sentence)
        return sentence

    def construct_sentence(self, start_char, end_char, region):
        from serif.theory.sentence import Sentence
        sentence = Sentence.from_values(owner=self, 
                                        start_char=start_char,
                                        end_char=end_char,
                                        region=region)
        sentence.document.generate_id(sentence)
        return sentence
