from serif.theory.serif_theory import SerifTheory
from serif.theory.enumerated_type import PredType

DEFINITIONAL_TYPES = { PredType.noun, PredType.pronoun, PredType.loc, PredType.set }
VERB_TYPES = { PredType.comp, PredType.copula, PredType.verb }

class SerifPropositionTheory(SerifTheory):
    
    def is_definitional(self):
        """Returns True if Proposition is of a definitional type"""
        return self.pred_type in DEFINITIONAL_TYPES

    def is_verbal(self):
        """Returns True if Proposition is of a verbal type"""
        return self.pred_type in VERB_TYPES

    def _get_summary(self):
        if self.head:
            pred = '%s:%s' % (self.pred_type.value,
                              self.head._get_summary())
        else:
            pred = self.pred_type.value
        return '%s(%s)' % (pred,
                           ', '.join(arg._get_summary()
                                     for arg in self.arguments))



