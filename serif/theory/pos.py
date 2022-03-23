from serif.theory.serif_theory import SerifTheory
from serif.theory.token import Token
from serif.xmlio import _SimpleAttribute, _ReferenceAttribute, _ChildTheoryElementList


class POS(SerifTheory):
    tag = _SimpleAttribute(is_required=False)
    prob = _SimpleAttribute(float, default=1.0)
    token = _ReferenceAttribute('token_id', cls=Token)
    alternate_pos_tags = _ChildTheoryElementList('AlternatePOS')
    upos = _SimpleAttribute()
    dep_rel = _SimpleAttribute()


    @classmethod
    def from_values(cls, owner, token, tag, upos=None, dep_rel=None):
        ret = cls(owner=owner)
        ret.token = token
        ret.tag = tag
        ret.prob = 1.0
        ret.upos = upos
        ret.dep_rel = dep_rel
        return ret

    @property
    def xpos(self):
        return self.tag