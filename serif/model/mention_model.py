from collections import defaultdict

import logging
from abc import abstractmethod
from serif.model.document_model import DocumentModel
from serif.model.validate import validate_sentence_tokens
from serif.theory.enumerated_type import MentionType

logger = logging.getLogger(__name__)


class MentionModel(DocumentModel):

    def __init__(self, **kwargs):
        super(MentionModel, self).__init__(**kwargs)
        self.modify_existing_mention = False
        if "modify_existing_mention" in kwargs:
            self.modify_existing_mention = True
        self.existing_mentions_by_span = defaultdict(list)
        self.existing_mentions_by_type_and_span = defaultdict(list)

    @abstractmethod
    def add_mentions_to_sentence(self, sentence):
        """
        :type sentence: Sentence
        :return: List where each element corresponds to a newly-added Mention.
        :rtype: list(Mention)
        """
        pass

    @staticmethod
    def add_new_mention(mention_set, entity_type, mention_type,
                        start_token, end_token, *, entity_subtype="UNDET", is_metonymy=False, intended_type=None,
                        role_type=None, link_confidence=None, confidence=None, parent_mention=None,
                        child_mention=None,
                        next_mention=None, model=None, pattern=None, coref_chain=None,
                        loose_synnode_constraint=False):
        """
        :type mention_set: MentionSet
        :type entity_type: string
        :type mention_type: string
        :type start_token: Token
        :type end_token: Token
        :type entity_subtype: string
        :type is_metonymy: bool
        :type intended_type: string
        :type role_type: string
        :type link_confidence: float
        :type confidence: float
        :type parent_mention: Mention
        :type child_mention: Mention
        :type next_mention: Mention
        :type model: string
        :type pattern: string
        :type coref_chain:
        :type loose_synnode_constraint: bool
        :return: List where each element corresponds to a newly-added Mention.
        :rtype: list(Mention)
        """
        # construct new mention
        if loose_synnode_constraint is True:
            syn_node = MentionModel.get_synnode_for_token_span(mention_set, "*", start_token, end_token)
        else:
            syn_node = MentionModel.get_synnode_for_token_span(mention_set, mention_type, start_token, end_token)
        if syn_node is not None and syn_node.start_token == start_token and syn_node.end_token == end_token:
            new_mention = mention_set.add_new_mention(syn_node, mention_type, entity_type)
        else:
            new_mention = mention_set.add_new_mention_from_tokens(mention_type, entity_type,
                                                                  start_token, end_token)
        if new_mention is not None:
            MentionModel.modify_mention_properties(new_mention, entity_subtype=entity_subtype, is_metonymy=is_metonymy,
                                                   intended_type=intended_type, role_type=role_type,
                                                   link_confidence=link_confidence, confidence=confidence,
                                                   parent_mention=parent_mention, child_mention=child_mention,
                                                   next_mention=next_mention, model=model, pattern=pattern,
                                                   coref_chain=coref_chain)
            return [new_mention]
        else:
            return []

    @staticmethod
    def modify_mention_properties(mention, *, entity_subtype="UNDET", is_metonymy=False, intended_type=None,
                                  role_type=None, link_confidence=None, confidence=None, parent_mention=None,
                                  child_mention=None, next_mention=None, model=None, pattern=None, coref_chain=None):
        if mention is not None:
            if entity_subtype != "UNDET":
                mention.entity_subtype = entity_subtype
            mention.is_metonymy = is_metonymy
            if intended_type is not None:
                mention.intended_type = intended_type
            if role_type is not None:
                mention.role_type = role_type
            if link_confidence is not None:
                mention.link_confidence = link_confidence
            if confidence is not None:
                mention.confidence = confidence
            if parent_mention is not None:
                mention.parent_mention = parent_mention
            if child_mention is not None:
                mention.child_mention = child_mention
            if next_mention is not None:
                mention.next_mention = next_mention
            if model is not None:
                mention.model = model
            if pattern is not None:
                mention.pattern = pattern
            if coref_chain is not None:
                mention.coref_chain = coref_chain

    def add_or_update_mention(self, mention_set, entity_type, mention_type,
                              start_token, end_token, *, entity_subtype="UNDET", is_metonymy=False, intended_type=None,
                              role_type=None, link_confidence=None, confidence=None, parent_mention=None,
                              child_mention=None, next_mention=None, model=None, pattern=None, coref_chain=None,
                              loose_synnode_constraint=False):
        """
        :type mention_set: MentionSet
        :type entity_type: string
        :type mention_type: string
        :type start_token: Token
        :type end_token: Token
        :type entity_subtype: string
        :type is_metonymy: bool
        :type intended_type: string
        :type role_type: string
        :type link_confidence: float
        :type confidence: float
        :type parent_mention: Mention
        :type child_mention: Mention
        :type next_mention: Mention
        :type model: string
        :type pattern: string
        :type coref_chain:
        :type loose_synnode_constraint: bool
        :return: List where each element corresponds to a newly-added or modified Mention.
        :rtype: list(Mention)
        """
        new_mentions = []

        span_key = start_token, end_token
        full_key = entity_type, mention_type == "NAME", start_token, end_token
        # check to see if mention already exists
        if self.modify_existing_mention and span_key in self.existing_mentions_by_span:
            for mention in self.existing_mentions_by_span.get(span_key):
                mention.entity_type = entity_type
                mention.mention_type = MentionType(mention_type.lower())
                MentionModel.modify_mention_properties(mention, entity_subtype=entity_subtype,
                                                       is_metonymy=is_metonymy,
                                                       intended_type=intended_type, role_type=role_type,
                                                       link_confidence=link_confidence, confidence=confidence,
                                                       parent_mention=parent_mention, child_mention=child_mention,
                                                       coref_chain=coref_chain,
                                                       next_mention=next_mention, model=model, pattern=pattern)
                new_mentions.append(mention)
        else:
            new_mentions_added = list()
            if full_key not in self.existing_mentions_by_type_and_span:
                # construct new mention
                new_mentions_added.extend(
                    MentionModel.add_new_mention(mention_set, entity_type, mention_type, start_token, end_token,
                                                 entity_subtype=entity_subtype, is_metonymy=is_metonymy,
                                                 intended_type=intended_type,
                                                 role_type=role_type, link_confidence=link_confidence,
                                                 confidence=confidence, parent_mention=parent_mention,
                                                 child_mention=child_mention,
                                                 next_mention=next_mention, model=model, pattern=pattern,
                                                 coref_chain=coref_chain,
                                                 loose_synnode_constraint=loose_synnode_constraint))
            # add it to the existing mention hash
            for new_mention in new_mentions_added:
                new_mentions.append(new_mention)
                self.existing_mentions_by_span[span_key].append(new_mention)
                self.existing_mentions_by_type_and_span[full_key].append(new_mention)

        return new_mentions

    @staticmethod
    def get_synnode_for_token_span(mention_set, mention_type, start_token, end_token):
        """
        :type mention_set: MentionSet
        :type mention_type: string
        :type start_token: Token
        :type end_token: Token
        :return: Smallest SynNode that covers the span from start_token to end_token, constrained by the set of
                valid SynNode tags for mention_type
        :rtype: SynNode
        """
        node = None
        if mention_set.parse is not None:
            if mention_type == "*" or mention_type == "NONE":
                node = mention_set.parse.get_covering_syn_node(start_token, end_token, [])
            elif mention_type == "NAME":
                node = mention_set.parse.get_covering_syn_node(start_token, end_token, ["NP"])
            elif mention_type == "DESC":
                node = mention_set.parse.get_covering_syn_node(start_token, end_token, ["NP"])
            elif mention_type == "PRON":
                node = mention_set.parse.get_covering_syn_node(start_token, end_token,
                                                               ["PRP", "PRP$", "WP", "WP$", "WDP"])
                np = mention_set.parse.get_covering_syn_node(start_token, end_token, ["NP"])
                # If there's an NP that contains only the pronoun, use that instead
                if np is not None and np.start_token == node.start_token and np.end_token == node.end_token:
                    node = np
            else:
                raise NotImplementedError("Cannot support mention_type {}".format(mention_type))
        return node

    def process_document(self, serif_doc):
        for i, sentence in enumerate(serif_doc.sentences):
            validate_sentence_tokens(sentence, serif_doc.docid, i)
            # Add an empty MentionSet
            if sentence.mention_set is None:
                sentence.add_new_mention_set()
                """:type: MentionSet"""

            # construct a hash of existing mentions
            self.existing_mentions_by_span.clear()
            self.existing_mentions_by_type_and_span.clear()

            for m in sentence.mention_set:
                tokens = m.tokens
                span_key = tokens[0], tokens[-1]
                full_key = m.entity_type, m.mention_type == "NAME", tokens[0], tokens[-1]
                self.existing_mentions_by_span[span_key].append(m)
                self.existing_mentions_by_type_and_span[full_key].append(m)

            self.add_mentions_to_sentence(sentence)
