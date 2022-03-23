import math
from abc import abstractmethod
from collections import defaultdict, Counter

from serif.model.actor_mention_model import ActorMentionModel
from serif.model.document_model import DocumentModel
from serif.model.validate import *


def sigmoid(x):
    '''squash actor entity scores into [0,1]'''
    return 1 / (1 + math.exp(-x))


class EntityLinkerModel(DocumentModel):
    def __init__(self, **kwargs):
        super(EntityLinkerModel, self).__init__(**kwargs)

    @abstractmethod
    def get_entity_link_info(self, doc_mentions, serif_doc):
        """
        :type doc_mentions: list[serifxml.theory.Mention]
        :return: List where each element corresponds to one entity link with a confidence. Each
                 element consists of an entity wiki-name string, and a float for the link confidence
        :rtype: list(tuple(str, float))  # TODO this can be extended to include db uid etc.
        """
        pass

    def add_entity_links_to_document(self, serif_doc):

        doc_mentions, e2m, m2e = self.get_mention_to_entity_info(serif_doc)
        e2l = defaultdict(list)  # store predicted links for entity

        entity_link_info = self.get_entity_link_info(doc_mentions, serif_doc)  # do prediction

        assert len(entity_link_info) == len(doc_mentions)

        # populates entities with their predicted links according to the mentions they govern
        for i, (link, score) in enumerate(entity_link_info):
            mention = doc_mentions[i]
            entities = m2e[mention]
            for entity in entities:
                e2l[entity].append((link, score))

        # constructs entity links in document
        for entity in e2m.keys():
            mentions_for_entity = e2m[entity]
            preds_for_entity = e2l[entity]
            assert len(mentions_for_entity) == len(preds_for_entity)
            self.resolve_predictions_for_entity(entity=entity,
                                                mentions_for_entity=mentions_for_entity,
                                                preds_for_entity=preds_for_entity,
                                                serif_doc=serif_doc)

    def resolve_predictions_for_entity(self, entity, mentions_for_entity, preds_for_entity, serif_doc):
        '''
        :param entity: serif.theory.Entity
        :param mentions_for_entity: list[serif.theory.Mention]
        :param preds_for_entity: list[(p, s)] where type(p)=str and type(s)=float

        Creates actor mentions based on predicted links, resolves the entity-level link and creates an actor entity
        '''
        assert len(mentions_for_entity) > 0

        actor_mentions_for_entity = []

        # create actor mention for each mention individually
        for i, mention in enumerate(mentions_for_entity):
            mention_wiki_name, mention_score = preds_for_entity[i][0], preds_for_entity[i][1]
            if serif_doc.sentences[mention.sent_no].actor_mention_set is None:
                serif_doc.sentences[mention.sent_no].add_new_actor_mention_set()
            if mention_wiki_name is not None:
                actor_mention_set = mention.sentence.actor_mention_set
                actor_mention = ActorMentionModel.add_new_actor_mention(
                    actor_mention_set=actor_mention_set,
                    mention=mention,
                    actor_db_name=mention_wiki_name,
                    actor_uid=-1,
                    actor_name=mention_wiki_name, source_note="entity_linker")
                actor_mentions_for_entity.append(actor_mention)

        # sum up predictions across mentions into aggregate predictions for entity
        # TODO adding up negative scores will worsen the score for predictions that appear several times with negative score; maybe that's ok if we squash with sigmoid?
        entity_l2s = Counter()
        for (link, score) in preds_for_entity:
            entity_l2s.update(Counter({link: score}))
        entity_predictions, entity_scores = zip(
            *list(sorted([(l, s) for l, s in entity_l2s.items()], key=lambda x: x[1], reverse=True)))

        # actor entity for entity-level link
        entity_wiki_name, entity_score = entity_predictions[0], entity_scores[0]
        if entity_wiki_name is not None:
            if serif_doc.actor_entity_set is None:
                serif_doc.add_new_actor_entity_set()
            serif_doc.actor_entity_set.add_new_actor_entity(entity=entity,
                                                            actor_uid=-1,
                                                            actor_mentions=actor_mentions_for_entity,
                                                            confidence=sigmoid(entity_score),  # squash with sigmoid
                                                            actor_name=entity_wiki_name)

    def get_mention_to_entity_info(self, serif_doc):
        '''
        :param serif_doc:
        :return: {Entity: list[Mention]},     # mentions goverened by entity
                 {Mention: list[Entity]},     # entities governing mention
                 list[Mention]                # deduplicated list of mentions over which to do linking
        '''
        mentions = []
        m2e = defaultdict(list)  # the same mention might be governed by more than one entity
        e2m = defaultdict(list)
        mentions_seen = set()
        for e in serif_doc.entity_set:
            for m in e.mentions:
                e2m[e].append(m)
                m2e[m].append(e)
                if m in mentions_seen:
                    continue
                mentions_seen.add(m)
                mentions.append(m)
        return mentions, e2m, m2e

    def process_document(self, serif_doc):
        for i, sentence in enumerate(serif_doc.sentences):
            validate_sentence_tokens(sentence, serif_doc.docid, i)
            validate_sentence_mention_sets(sentence, serif_doc.docid, i)
        self.add_entity_links_to_document(serif_doc)
