from serif.theory.serif_parse_theory import SerifParseTheory
from serif.theory.token_sequence import TokenSequence
from serif.xmlio import _SimpleAttribute, _ReferenceAttribute, _ChildTextElement, _ChildTheoryElement

class Parse(SerifParseTheory):
    score = _SimpleAttribute(float)
    token_sequence = _ReferenceAttribute('token_sequence_id',
                                         cls=TokenSequence)
    root = _ChildTheoryElement('SynNode')
    _treebank_string = _ChildTextElement('TreebankString')

    @classmethod
    def from_values(cls, owner=None, score=score, token_sequence=None, treebank_string=None):
        ret = cls(owner=owner)
        ret.document.generate_id(ret)
        ret.set_score(score)
        ret.set_token_sequence(token_sequence)
        ret.set_treebank_string(treebank_string)
        ret._parse_treebank_string()
        return ret

    def set_score(self, score):
        self.score = score

    def set_token_sequence(self, token_sequence):
        self.token_sequence = token_sequence

    # def add_treebank_string(self, treebank_string):
    #     self._treebank_string.append(treebank_string)

    def set_treebank_string(self, treebank_string):
        self._treebank_string = treebank_string

