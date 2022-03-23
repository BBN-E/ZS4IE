from abc import abstractmethod

from serif.model.document_model import DocumentModel
from serif.model.validate import *


class RelationMentionModel(DocumentModel):

    def __init__(self, **kwargs):
        super(RelationMentionModel, self).__init__(**kwargs)
        self.relation_key_to_relation = dict()

    @abstractmethod
    def add_relation_mentions_to_sentence(self, sentence):
        """
        :type sentence: Sentence
        :return: List where each element corresponds to one newly-added RelMention.
        :rtype: list(RelMention)
        """
        pass

    @staticmethod
    def modify_relation_mention_properties(rel_mention, *,
                                           pattern=None, score=None, confidence=None, raw_type=None, time_arg=None,
                                           time_arg_role=None, time_arg_score=None, model=None):
        if pattern is not None:
            rel_mention.pattern = pattern
        if score is not None:
            rel_mention.score = score
        if confidence is not None:
            rel_mention.confidence = confidence
        if raw_type is not None:
            rel_mention.raw_type = raw_type
        if time_arg is not None:
            rel_mention.time_arg = time_arg
        if time_arg_role is not None:
            rel_mention.time_arg_role = time_arg_role
        if time_arg_score is not None:
            rel_mention.time_arg_score = time_arg_score
        if model is not None:
            rel_mention.model = model

    @staticmethod
    def add_new_relation_mention(rel_mention_set, rel_type, l_mention, r_mention, tense, modality, *,
                                 pattern=None, score=None, confidence=None, raw_type=None, time_arg=None,
                                 time_arg_role=None, time_arg_score=None, model=None):
        """
        :type rel_mention_set: RelMentionSet
        :type rel_type: string
        :type l_mention: Mention
        :type r_mention: Mention
        :type tense: Tense
        :type modality: Modality
        :type pattern: string
        :type score: float
        :type confidence: float
        :type raw_type: string
        :type time_arg: ValueMention
        :type time_arg_role: string
        :type time_arg_score: float
        :return: List where each element corresponds to one newly-added RelMention.
        :rtype: list(RelMention)
        """
        rel_mention = rel_mention_set.add_new_relation_mention(
            l_mention, r_mention, rel_type, tense, modality)
        RelationMentionModel.modify_relation_mention_properties(rel_mention, pattern=pattern, score=score,
                                                                confidence=confidence, raw_type=raw_type,
                                                                time_arg=time_arg, time_arg_role=time_arg_role,
                                                                time_arg_score=time_arg_score, model=model)
        return [rel_mention]

    def add_or_update_relation_mention(self, rel_mention_set, rel_type, l_mention, r_mention, tense, modality, *,
                                       pattern=None, score=None, confidence=None, raw_type=None, time_arg=None,
                                       time_arg_role=None, time_arg_score=None, model=None):

        # get objects to add
        rel_mentions = []
        # if it exists, don't add it
        rel_mention_key = rel_type, l_mention, r_mention
        if rel_mention_key in self.relation_key_to_relation:
            existing_rel_mentions = self.relation_key_to_relation[rel_mention_key]
            for rel_mention in existing_rel_mentions:
                RelationMentionModel.modify_relation_mention_properties(rel_mention, pattern=pattern, score=score,
                                                                        confidence=confidence, raw_type=raw_type,
                                                                        time_arg=time_arg, time_arg_role=time_arg_role,
                                                                        time_arg_score=time_arg_score, model=model)
            rel_mentions.extend(existing_rel_mentions)
        else:
            # construct object
            rel_mention_added = RelationMentionModel.add_new_relation_mention(rel_mention_set, rel_type, l_mention,
                                                                              r_mention, tense, modality,
                                                                              pattern=pattern, score=score,
                                                                              confidence=confidence,
                                                                              raw_type=raw_type, time_arg=time_arg,
                                                                              time_arg_role=time_arg_role,
                                                                              time_arg_score=time_arg_score,
                                                                              model=model)
            for rel_mention in rel_mention_added:
                self.relation_key_to_relation.setdefault(rel_mention_key, list()).append(rel_mention)
            rel_mentions.extend(rel_mention_added)
        return rel_mentions

    def process_document(self, serif_doc):
        for i, sentence in enumerate(serif_doc.sentences):
            validate_sentence_tokens(sentence, serif_doc.docid, i)
            validate_sentence_mention_sets(sentence, serif_doc.docid, i)
            rel_mention_set = sentence.rel_mention_set
            if rel_mention_set is None:
                rel_mention_set = \
                    sentence.add_new_relation_mention_set()
                ''':type: RelMentionSet'''
            self.relation_key_to_relation.clear()
            for rel_mention in rel_mention_set:
                rel_mention_key = rel_mention.type, rel_mention.left_mention, rel_mention.right_mention
                self.relation_key_to_relation.setdefault(rel_mention_key, list()).append(rel_mention)
            self.add_relation_mentions_to_sentence(sentence)
