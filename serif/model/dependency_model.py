from abc import abstractmethod

from serif.model.document_model import DocumentModel
from serif.model.validate import *
from serif.theory.mention import Mention
from serif.theory.syn_node import SynNode
from serif.theory.proposition import Proposition


class DependencyModel(DocumentModel):

    def __init__(self, **kwargs):
        super(DependencyModel, self).__init__(**kwargs)

    @abstractmethod
    def add_dependencies_to_sentence(self, sentence):
        pass

    @staticmethod
    def add_new_proposition(dependency_set, pred_type, head_node, *, particle=None, adverb=None, negation=None,
                            modal=None, statuses=None):
        new_proposition = dependency_set.add_new_proposition(pred_type, head_node)
        new_proposition.particle = particle
        new_proposition.adverb = adverb
        new_proposition.negation = negation
        new_proposition.modal = modal
        new_proposition.statuses = statuses
        return [new_proposition]

    @staticmethod
    def add_new_argument(proposition, role, theory_obj):
        if isinstance(theory_obj, SynNode):
            return [proposition.add_new_synnode_argument(role, theory_obj)]
        elif isinstance(theory_obj, Mention):
            return [proposition.add_new_mention_argument(role, theory_obj)]
        elif isinstance(theory_obj, Proposition):
            return [proposition.add_new_proposition_argument(role, theory_obj)]
        else:
            raise NotImplementedError("Cannot support {}".format(type(theory_obj)))

    def process_document(self, serif_doc):
        for i, sentence in enumerate(serif_doc.sentences):
            validate_sentence_tokens(sentence, serif_doc.docid, i)
            # validate_sentence_mention_sets(sentence, serif_doc.docid, i)
            # Since we can set max_tokens, we can now end up without a 
            # MentionSet
            if sentence.mention_set is None:
                sentence.add_new_mention_set()
            if sentence.dependency_set is None:
                sentence.add_new_dependency_set(sentence.mention_set)
            self.add_dependencies_to_sentence(sentence)
