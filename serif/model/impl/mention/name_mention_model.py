from serif.model.mention_model import MentionModel
import logging

logger = logging.getLogger(__name__)


class NameMentionModel(MentionModel):
    """Makes Mentions for existing Names"""

    def __init__(self,**kwargs):
        super(NameMentionModel,self).__init__(**kwargs)

    def add_mentions_to_sentence(self, sentence):
        new_mentions = []
        if sentence.name_theory is None:
            logger.warning("No name theory for sentence {}, skipping NameMentionModel".
                           format(sentence.id))
        else:
            mention_type = "NAME"
            for name in sentence.name_theory:
                new_mentions.extend(self.add_or_update_mention(sentence.mention_set, name.entity_type, mention_type,
                                                               name.start_token, name.end_token,
                                                               loose_synnode_constraint=True))
        return new_mentions
