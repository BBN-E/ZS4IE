from serif.model.mention_model import MentionModel


class EmptyMentionSetModel(MentionModel):
    """Adds empty mention set to sentence. 
       Depenency parses rely on having a mention set, so this could be
       necessary even if you don't care about mentions."""

    def __init__(self, **kwargs):
        super(EmptyMentionSetModel, self).__init__(**kwargs)

    def add_mentions_to_sentence(self, sentence):
        return []
