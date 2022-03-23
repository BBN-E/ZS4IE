import logging
from abc import abstractmethod

from serif.model.document_model import DocumentModel
from serif.model.validate import *
from serif.model.value_mention_model import ValueMentionModel

logger = logging.getLogger(__name__)


class TimeValueMentionModel(DocumentModel):

    def __init__(self, timeout=-1, max_sents_per_doc=-1, **kwargs):
        self.max_sents_per_doc = int(max_sents_per_doc)
        super(TimeValueMentionModel, self).__init__(**kwargs)

    @abstractmethod
    def add_time_value_mentions_to_sentence(self, sentence):
        pass

    def add_new_time_value(self, value_mention_set, value_set, start_token, end_token, timex_string):
        assert start_token.sentence is end_token.sentence
        sent_no = start_token.sentence.sent_no
        # For the return value
        added_value_mentions = []
        added_values = []
        # Add ValueMentions to value_mention_set

        # Check to see if this already exists, if so,
        # don't add it
        value_type = "TIMEX2.TIME"
        hash_key = value_type, start_token, end_token
        if hash_key in self.value_mention_hash_to_value_mentions:
            added_value_mentions.extend(self.value_mention_hash_to_value_mentions[hash_key])
        else:
            new_value_mentions = ValueMentionModel.add_new_value_mention(value_mention_set, value_type,
                                                                         start_token, end_token, sent_no=sent_no)
            for value_mention in new_value_mentions:
                self.value_mention_hash_to_value_mentions.setdefault(hash_key, list()).append(value_mention)
                added_value_mentions.append(value_mention)
        for value_mention in added_value_mentions:
            value_mention.sent_no = sent_no
            # Add ValueMention to Value
            value = value_set.add_new_value(value_mention=value_mention,
                                            value_type=value_type,
                                            timex_string=timex_string)
            added_values.append(value)
        return added_value_mentions, added_values

    def process_document(self, serif_doc):

        if serif_doc.value_set is None:
            serif_doc.add_new_value_set()
        print("# sentences in doc = {}".format(len(serif_doc.sentences)))
        if self.max_sents_per_doc > 0 and len(serif_doc.sentences) < self.max_sents_per_doc:
            for i, sentence in enumerate(serif_doc.sentences):
                validate_sentence_tokens(sentence, serif_doc.docid, i)
                if sentence.value_mention_set is None:
                    sentence.add_new_value_mention_set()
                self.value_mention_hash_to_value_mentions = dict()
                for vm in sentence.value_mention_set:
                    hash_key = (vm.value_type, vm.start_token, vm.end_token)
                    self.value_mention_hash_to_value_mentions.setdefault(hash_key, list()).append(vm)
                self.add_time_value_mentions_to_sentence(sentence)

