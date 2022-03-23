from abc import abstractmethod

from serif.model.document_model import DocumentModel
from serif.theory.pos import POS
from serif.model.validate import *


class PartOfSpeechModel(DocumentModel):

    def __init__(self, **kwargs):
        super(PartOfSpeechModel, self).__init__(**kwargs)

    @abstractmethod
    def add_pos_to_sentence(self, sentence):
        """
        :type Sentence: sentence
        :return: List where each element corresponds to one POS.
        :rtype: list(POS)
        """
        pass

    @staticmethod
    def add_new_pos(pos_sequence, token, tag, *, upos=None, dep_rel=None):
        assert token.index() == len(pos_sequence)
        return [pos_sequence.add_new_pos(token, tag, upos, dep_rel)]

    def process_document(self, serif_doc):
        validate_doc_sentences(serif_doc)
        for i, sentence in enumerate(serif_doc.sentences):
            validate_sentence_tokens(sentence, serif_doc.docid, i)
            part_of_speech_sequence = sentence.add_new_part_of_speech_sequence()
            part_of_speech_sequence.set_score(0.7)
            self.add_pos_to_sentence(sentence)
