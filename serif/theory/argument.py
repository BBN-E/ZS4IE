from serif.theory.mention import Mention
from serif.theory.proposition import Proposition
from serif.theory.serif_theory import SerifTheory
from serif.theory.syn_node import SynNode
from serif.xmlio import _SimpleAttribute, _ReferenceAttribute


class Argument(SerifTheory):
    role = _SimpleAttribute()
    mention = _ReferenceAttribute('mention_id', cls=Mention)
    syn_node = _ReferenceAttribute('syn_node_id', cls=SynNode)
    proposition = _ReferenceAttribute('proposition_id', cls=Proposition)

    value = property(
        lambda self: self.mention or self.syn_node or self.proposition)

    def _get_summary(self):
        return '%s=%r' % (self.role or '<val>', self.value)
