import re
from abc import abstractmethod
from serif.model.document_model import DocumentModel
from serif.model.validate import *


class ParserModel(DocumentModel):

    def __init__(self, **kwargs):
        super(ParserModel, self).__init__(**kwargs)
        self.add_heads = False
        if "add_heads" in kwargs:
            self.add_heads = True

    @abstractmethod
    def add_parse_to_sentence(self, serif_sentence):
        pass

    def add_new_parse(self, sentence, treebank_string, score=0.9):
        ret = list()
        if treebank_string is not None:
            parse = sentence.add_new_parse(
                score, sentence.token_sequence,
                re.sub(pattern="\s+", repl=" ", string=treebank_string))
            if self.add_heads:
                parse.add_heads()
            ret.append(parse)

    def process_document(self, serif_doc):
        for i, sentence in enumerate(serif_doc.sentences):
            validate_sentence_tokens(sentence, serif_doc.docid, i)
            self.add_parse_to_sentence(sentence)
