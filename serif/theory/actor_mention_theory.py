from serif.theory.serif_theory import SerifTheory


class ActorMentionTheory(SerifTheory):
    @property
    def text(self):
        """The original text substring covered by this event participant"""
        return self.mention.text

    def _get_summary(self):
        return repr(self.text)
