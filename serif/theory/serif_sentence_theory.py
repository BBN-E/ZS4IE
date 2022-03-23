from serif.theory.sentences import Sentences
from serif.theory.serif_offset_theory import SerifOffsetTheory
from serif.util import _raise_expected_exactly_one_error


class SerifSentenceTheory(SerifOffsetTheory):
    def save_text(self):
        if self.contents is None:
            self.contents = self.text

    @property
    def sent_no(self):
        """
        The index of this sentence in the 'Sentences' that owns it, or
        None if this sentence is not owned by a 'Sentences'.
        """
        if isinstance(self.owner, Sentences):
            return self.owner.index(self)

    def _get_sentence_theory(self):
        if len(self._sentence_theories) == 0:
            return None
        elif len(self._sentence_theories) == 1:
            return self._sentence_theories[0]
        else:
            _raise_expected_exactly_one_error(
                'Sentence', 'sentence_theory', 'sentence_theories',
                len(self._sentence_theories))

    def _set_sentence_theory(self, value):
        if value is None:
            self._sentence_theories = []
        else:
            self._sentence_theories = [value, ]

    sentence_theory = property(_get_sentence_theory,
                               _set_sentence_theory, doc="""
        The unique sentence_theory for this sentence, or None if the
        sentence has no sentence_theory.  If the sentence has multiple
        candidate sentence_theories, then this will raise an
        exception.""")

    def get_dependency_info(self):
        if self.dependency_set is None:
            return None
        return self.dependency_set.get_dependency_info(
            self.mention_set, self.value_mention_set, self.event_mention_set)

