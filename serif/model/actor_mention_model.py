import logging
from abc import abstractmethod

from serif.model.document_model import DocumentModel

# This model is for creating and filling 
# a sentence-level ActorMentionSet. There is also
# a document-level ActorMentionSet used for ICEWS 
# stuff. See:
# https://collab.bbn.com/confluence/display/AMIWEB/Actor+matching+in+CSERIF
# for details on the two different ActorMentionSets.

logger = logging.getLogger(__name__)


class ActorMentionModel(DocumentModel):

    def __init__(self, **kwargs):
        super(ActorMentionModel, self).__init__(**kwargs)

    # This API just covers the bare minimum of fields for 
    # an ActorMention, which has a huge number of possible
    # fields. But filling in all those fields should wait until
    # the redesign described here is done:
    # https://ami-gitlab-01.bbn.com/text-group/text-open/-/issues/89
    @abstractmethod
    def add_actor_mentions_to_sentence(self, sentence):
        """
        :type sentence: Sentence
        :return: List where each element corresponds to newly added ActorMention.
        :rtype: list(ActorMention)
        """
        pass

    @staticmethod
    def add_new_actor_mention(actor_mention_set, mention, actor_db_name, actor_uid, actor_name, source_note, *,
                              sentence_theory=None, actor_code=None, actor_pattern_uid=None, is_acronym=None,
                              requires_context=None, pattern_confidence_score=None, importance_score=None,
                              paired_actor_uid=None, paired_actor_code=None, paired_actor_pattern_uid=None,
                              paired_actor_name=None, paired_agent_uid=None, paired_agent_code=None,
                              paired_agent_pattern_uid=None, paired_agent_name=None, actor_agent_pattern=None,
                              geo_country=None, geo_latitude=None, geo_longitude=None, geo_uid=None, geo_text=None,
                              country_id=None, iso_code=None, country_info_actor_id=None, country_info_actor_code=None,
                              pattern_match_score=None, association_score=None, edit_distance_score=None,
                              georesolution_score=None, confidence=None, name=None):
        actor_mentions = []
        actor_mention = actor_mention_set.add_new_actor_mention(mention, actor_db_name, actor_uid, actor_name,
                                                                source_note)
        actor_mention.sentence_theory = sentence_theory
        actor_mention.actor_code = actor_code
        actor_mention.actor_pattern_uid = actor_pattern_uid
        actor_mention.is_acronym = is_acronym
        actor_mention.requires_context = requires_context
        actor_mention.pattern_confidence_score = pattern_confidence_score
        actor_mention.importance_score = importance_score
        actor_mention.paired_actor_uid = paired_actor_uid
        actor_mention.paired_actor_code = paired_actor_code
        actor_mention.paired_actor_pattern_uid = paired_actor_pattern_uid
        actor_mention.paired_actor_name = paired_actor_name
        actor_mention.paired_agent_uid = paired_agent_uid
        actor_mention.paired_agent_code = paired_agent_code
        actor_mention.paired_agent_pattern_uid = paired_agent_pattern_uid
        actor_mention.paired_agent_name = paired_agent_name
        actor_mention.actor_agent_pattern = actor_agent_pattern
        actor_mention.geo_country = geo_country
        actor_mention.geo_latitude = geo_latitude
        actor_mention.geo_longitude = geo_longitude
        actor_mention.geo_uid = geo_uid
        actor_mention.geo_text = geo_text
        actor_mention.country_id = country_id
        actor_mention.iso_code = iso_code
        actor_mention.country_info_actor_id = country_info_actor_id
        actor_mention.country_info_actor_code = country_info_actor_code
        actor_mention.pattern_match_score = pattern_match_score
        actor_mention.association_score = association_score
        actor_mention.edit_distance_score = edit_distance_score
        actor_mention.georesolution_score = georesolution_score
        actor_mention.confidence = confidence
        actor_mention.name = name
        actor_mentions.append(actor_mention)
        return actor_mentions

    def process_document(self, serif_doc):
        for i, sentence in enumerate(serif_doc.sentences):
            if sentence.actor_mention_set is None:
                actor_mention_set = sentence.add_new_actor_mention_set()
            self.add_actor_mentions_to_sentence(sentence)
