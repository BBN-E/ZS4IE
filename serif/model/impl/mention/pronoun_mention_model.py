from serif.model.mention_model import MentionModel
import logging

logger = logging.getLogger(__name__)


class PronounMentionModel(MentionModel):
    """Creates a Mention for each Pronoun"""

    def __init__(self, **kwargs):
        super(PronounMentionModel, self).__init__(**kwargs)

    def add_mentions_to_sentence(self, sentence):
        new_mentions = []
        if sentence.parse is None:
            logger.warning("No parse for sentence {}, skipping PronounMentionModel".
                           format(sentence.id))
        else:
            nodes = sentence.parse.get_nodes_matching_tags(["PRP", "PRP$", "WP", "WP$", "WDP"])
            for node in nodes:
                new_mentions.extend(self.add_or_update_mention(sentence.mention_set, 'UNDET', 'PRON',
                                                               node.start_token, node.end_token,
                                                               model=type(self).__name__))
        return new_mentions
