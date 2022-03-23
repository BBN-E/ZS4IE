import logging
from abc import abstractmethod

from serif.model.document_model import DocumentModel
from serif.model.validate import *

logger = logging.getLogger(__name__)


class ValueMentionModel(DocumentModel):

    def __init__(self, **kwargs):
        super(ValueMentionModel, self).__init__(**kwargs)
        self.value_mention_hash_to_value_mentions = dict()

    @abstractmethod
    def add_value_mentions_to_sentence(self, sentence):
        """
        :type sentence: Sentence
        :return: List where each element corresponds to one ValueMention.
        :rtype: list(tuple(str, Token, Token))
        """
        pass

    @staticmethod
    def modify_value_mention_properties(value_mention, *, sent_no=None):
        if sent_no is not None:
            value_mention.sent_no = sent_no

    @staticmethod
    def add_new_value_mention(value_mention_set, value_type, start_token, end_token, *, sent_no=None):
        value_mention = value_mention_set.add_new_value_mention(
            start_token, end_token, value_type)
        ValueMentionModel.modify_value_mention_properties(value_mention, sent_no=sent_no)
        return [value_mention]

    def add_or_update_value_mention(self, value_mention_set, value_type, start_token, end_token, *, sent_no=None):
        # For the return value
        added_value_mentions = []

        # Add ValueMentions to value_mention_set

        # Check to see if this already exists, if so,
        # don't add it
        hash_key = value_type, start_token, end_token
        if hash_key in self.value_mention_hash_to_value_mentions:
            existing_values = self.value_mention_hash_to_value_mentions[hash_key]
            for value_mention in existing_values:
                ValueMentionModel.modify_value_mention_properties(value_mention, sent_no=sent_no)
                added_value_mentions.append(value_mention)
        else:
            new_value_mentions = ValueMentionModel.add_new_value_mention(value_mention_set, value_type,
                                                                         start_token, end_token, sent_no=sent_no)
            for value_mention in new_value_mentions:
                self.value_mention_hash_to_value_mentions.setdefault(hash_key, list()).append(value_mention)
                added_value_mentions.append(value_mention)
        return added_value_mentions

    def process_document(self, serif_doc):
        for i, sentence in enumerate(serif_doc.sentences):
            validate_sentence_tokens(sentence, serif_doc.docid, i)
            if sentence.value_mention_set is None:
                sentence.add_new_value_mention_set()
            self.value_mention_hash_to_value_mentions.clear()
            for vm in sentence.value_mention_set:
                hash_key = (vm.value_type, vm.start_token, vm.end_token)
                self.value_mention_hash_to_value_mentions.setdefault(hash_key, list()).append(vm)
            self.add_value_mentions_to_sentence(sentence)
