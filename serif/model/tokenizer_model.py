from abc import abstractmethod

from serif.model.document_model import DocumentModel


class TokenizerModel(DocumentModel):

    def __init__(self, **kwargs):
        super(TokenizerModel, self).__init__(**kwargs)

    @abstractmethod
    def add_tokens_to_sentence(self, sentence):
        """
        :type sentence: sentence
        :return: List where each element corresponds to one Token.
        :rtype: list(tuple(str, int, int))
        """
        pass

    @staticmethod
    def add_new_token(token_sequence, tokenized_text, start_char, end_char, *, lemma=None, original_token_index=None):
        new_token = token_sequence.add_new_token(start_char, end_char, tokenized_text, lemma=lemma)
        new_token.original_token_index = original_token_index
        return [new_token]

    @staticmethod
    def add_token_head(token, head_token):
        assert token.owner == head_token.owner
        token.head = head_token

    def process_document(self, serif_doc):
        for sentence in serif_doc.sentences:
            token_sequence = sentence.add_new_token_sequence()
            self.add_tokens_to_sentence(sentence)
