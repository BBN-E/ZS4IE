from serif.theory.serif_offset_theory import SerifOffsetTheory


class SerifValueMentionTheory(SerifOffsetTheory):
    @property
    def tokens(self):
        s = self.start_token.index()
        e = self.end_token.index()
        return self.sentence.token_sequence[s:e + 1]

    def get_normalized_time(self):
        """If this is a time ValueMention, return the normalized time
           (if any) from the Value object that contains it. Otherwise
           return None.
        """
        doc = self.document
        for value in doc.value_set or list():
            if value.value_mention == self:
                return value.timex_val
        return None
