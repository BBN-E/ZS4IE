from abc import abstractmethod

from serif.model.document_model import DocumentModel


class SentenceSplitterModel(DocumentModel):
    def __init__(self, **kwargs):
        super(SentenceSplitterModel, self).__init__(**kwargs)

    @abstractmethod
    def add_sentences_to_document(self, serif_doc, region):
        pass

    @staticmethod
    def add_new_sentence(sentences, region, sent_start_char, sent_end_char):
        return [
            sentences.add_new_sentence(start_char=sent_start_char, end_char=sent_end_char, region=region)]

    def process_document(self, serif_doc):
        sentences = serif_doc.add_new_sentences()
        for region in serif_doc.regions:
            self.add_sentences_to_document(serif_doc, region)
