from serif.theory.serif_token_theory import SerifTokenTheory
from serif.xmlio import _ReferenceListAttribute, _SimpleAttribute, _TextOfElement, _ReferenceAttribute


class Token(SerifTokenTheory):
    # note: default value for text is extracted from the original string.
    text = _TextOfElement(strip=True)
    lexical_entries = _ReferenceListAttribute('lexical_entries',
                                              cls='LexicalEntry')
    original_token_index = _SimpleAttribute(int)
    head = _ReferenceAttribute('head_token_id',
                               cls="Token")
    lemma = _SimpleAttribute()

    @classmethod
    def from_values(cls, owner=None, start_char=0, end_char=0, text=None, lemma=None):
        ret = cls(owner=owner)
        ret.set_offset(start_char, end_char)
        ret.set_text(text)
        ret.lemma = lemma
        return ret

    def set_text(self, text):
        self.text = text

    def get_hosting_sentence_theory(self):
        token_sequence = self.owner
        for sentence_theory in token_sequence.sentence.sentence_theories:
            if sentence_theory.token_sequence == token_sequence:
                return sentence_theory
        return None

    @property
    def upos(self):
        pos = self.pos
        if pos is not None:
            return pos.upos
        return None

    @property
    def pos(self):
        hosting_sentence_theory = self.get_hosting_sentence_theory()
        if hosting_sentence_theory:
            if hosting_sentence_theory.pos_sequence and len(hosting_sentence_theory.pos_sequence) > self.index():
                return hosting_sentence_theory.pos_sequence[self.index()]
        return None

    @property
    def xpos(self):
        pos = self.pos
        if pos is not None:
            return pos.xpos
        return None

    @property
    def dep_rel(self):
        pos = self.pos
        if pos is not None:
            return pos.dep_rel
        return None
