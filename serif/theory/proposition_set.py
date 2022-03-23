from serif.theory.enumerated_type import PredType
from serif.theory.mention_set import MentionSet
from serif.theory.proposition import Proposition
from serif.theory.serif_sequence_theory import SerifSequenceTheory
from serif.xmlio import _ReferenceAttribute, _ChildTheoryElementList


class PropositionSet(SerifSequenceTheory):
    mention_set = _ReferenceAttribute('mention_set_id', cls=MentionSet)
    _children = _ChildTheoryElementList('Proposition')

    @classmethod
    def from_values(cls, owner=None, mention_set=None):
        ret = cls(owner=owner)
        ret.mention_set = mention_set
        return ret

    @classmethod
    def empty(cls, owner=None, mention_set=None):
        return cls.from_values(owner=owner, mention_set=mention_set)

    def add_proposition(self, proposition):
        self._children.append(proposition)

    def add_new_proposition(self, pred_type, head_node):
        proposition = self.construct_proposition(pred_type, head_node)
        self.add_proposition(proposition)
        return proposition

    def construct_proposition(self, pred_type, head_node):
        proposition = Proposition(owner=self)
        proposition.head = head_node
        upt = pred_type.upper()
        if upt == "VERB":
            proposition.pred_type = PredType.verb
        elif upt == "COPULA":
            proposition.pred_type = PredType.copula
        elif upt == "MODIFIER":
            proposition.pred_type = PredType.modifier
        elif upt == "NOUN":
            proposition.pred_type = PredType.noun
        elif upt == "POSS":
            proposition.pred_type = PredType.poss
        elif upt == "LOC":
            proposition.pred_type = PredType.loc
        elif upt == "SET":
            proposition.pred_type = PredType.set
        elif upt == "NAME":
            proposition.pred_type = PredType.name
        elif upt == "PRONOUN":
            proposition.pred_type = PredType.pronoun
        elif upt == "COMP":
            proposition.pred_type = PredType.comp
        elif upt == "DEPENDENCY":
            proposition.pred_type = PredType.dependency
        else:
            raise Exception("Unknown pred_type: " + pred_type)
        proposition.document.generate_id(proposition)
        return proposition
