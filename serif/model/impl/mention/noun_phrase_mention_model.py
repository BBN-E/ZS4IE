import logging

from serif.model.mention_model import MentionModel

logger = logging.getLogger(__name__)


class NounPhraseMentionModel(MentionModel):
    """Creates a Mention for each NP"""

    def __init__(self, **kwargs):
        super(NounPhraseMentionModel, self).__init__(**kwargs)

    def add_mentions_to_sentence(self, sentence):
        new_mentions = []
        if sentence.parse is None:
            logger.warning("No parse for sentence {}, skipping NounPhraseMentionModel".
                           format(sentence.id))
        else:
            nodes = sentence.parse.get_nodes_matching_tags(["NP"])
            for node in nodes:
                new_mentions.extend(self.add_or_update_mention(sentence.mention_set, 'UNDET', 'DESC',
                                                               node.start_token, node.end_token,
                                                               model=type(self).__name__))

        return new_mentions
