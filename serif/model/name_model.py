from abc import abstractmethod

from serif.model.document_model import DocumentModel
from serif.model.validate import *


class NameModel(DocumentModel):

    def __init__(self, **kwargs):
        super(NameModel, self).__init__(**kwargs)
        self.name_hash = dict()

    @abstractmethod
    def add_names_to_sentence(self, serif_sentence):
        pass

    @staticmethod
    def modify_name_properties(name, *, transliteration=None, score=None):
        if transliteration is not None:
            name.transliteration = transliteration
        if score is not None:
            name.score = score

    @staticmethod
    def add_new_name(name_theory, entity_type, start_token, end_token, *, transliteration=None, score=None):
        """
        :type name_theory: NameTheory
        :type entity_type: string
        :type start_token: Token
        :type end_token: Token
        :type transliteration: string
        :type score: float
        :return: List where each element corresponds to a newly-added Name.
        :rtype: list(Name)
        """
        name = name_theory.add_new_name(
            entity_type, start_token, end_token)
        NameModel.modify_name_properties(name, transliteration=transliteration, score=score)
        return [name]

    def add_or_update_name(self, name_theory, entity_type, start_token, end_token, *, transliteration=None, score=None):
        # Build NameTheory if necessary (doc not invalid, just needs more work)
        names = []

        # if it exists, don't add it
        name_key = (entity_type, start_token, end_token)
        if name_key in self.name_hash:
            existing_names = self.name_hash[name_key]
            for existing_name in existing_names:
                NameModel.modify_name_properties(existing_name, transliteration, score)
                names.append(existing_name)
        else:
            names_added = NameModel.add_new_name(name_theory, entity_type, start_token, end_token,
                                                 transliteration=transliteration, score=score)
            for name in names_added:
                names.append(name)
                self.name_hash.setdefault(name_key, list()).append(name)
        return names

    def process_document(self, serif_doc):
        for i, sentence in enumerate(serif_doc.sentences):
            validate_sentence_tokens(sentence, serif_doc.docid, i)
            name_theory = sentence.name_theory
            if name_theory is None:
                name_theory = sentence.add_new_name_theory()
            self.name_hash.clear()
            for n in name_theory:
                self.name_hash.setdefault((n.entity_type, n.start_token, n.end_token), list()).append(n)
            self.add_names_to_sentence(sentence)
