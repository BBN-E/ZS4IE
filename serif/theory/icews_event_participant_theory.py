from serif.theory.serif_theory import SerifTheory


class ICEWSEventParticipantTheory(SerifTheory):
    @property
    def text(self):
        """The original text substring covered by this event participant"""
        return self.actor.text

    @property
    def mention(self):
        """Shortcut for self.actor.mention"""
        return self.actor.mention

    @property
    def sentence_theory(self):
        """Shortcut for self.actor.sentence_theory"""
        return self.actor.sentence_theory

    def _get_summary(self):
        return repr(self.text)
