from serif.theory.enumerated_type import PredType, PropStatus
from serif.theory.serif_proposition_theory import SerifPropositionTheory
from serif.theory.syn_node import SynNode
from serif.xmlio import _ChildTheoryElementList, _SimpleAttribute, _ReferenceAttribute, _SimpleListAttribute

class Proposition(SerifPropositionTheory):
    arguments = _ChildTheoryElementList('Argument')
    pred_type = _SimpleAttribute(PredType, attr_name='type',
                                 is_required=True)
    head = _ReferenceAttribute('head_id', cls=SynNode)
    particle = _ReferenceAttribute('particle_id', cls=SynNode)
    adverb = _ReferenceAttribute('adverb_id', cls=SynNode)
    negation = _ReferenceAttribute('negation_id', cls=SynNode)
    modal = _ReferenceAttribute('modal_id', cls=SynNode)
    statuses = _SimpleListAttribute(PropStatus, attr_name='status')

    def add_argument(self, argument):
        self.arguments.append(argument)

    def add_new_synnode_argument(self, role, synnode):
        argument = self.construct_argument(role, synnode, None, None)
        self.add_argument(argument)
        return argument

    def add_new_mention_argument(self, role, mention):
        argument = self.construct_argument(role, None, mention, None)
        self.add_argument(argument)
        return argument

    def add_new_proposition_argument(self, role, proposition):
        argument = self.construct_argument(role, None, None, proposition)
        self.add_argument(argument)
        return argument

    def construct_argument(self, role, synnode, mention, proposition):
        from serif.theory.argument import Argument
        argument = Argument(owner=self)
        argument.role = role
        argument.syn_node = synnode
        argument.mention = mention
        argument.proposition = proposition
        argument.document.generate_id(argument)
        return argument
