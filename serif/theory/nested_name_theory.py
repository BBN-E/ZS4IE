from serif.theory.name_theory import NameTheory
from serif.xmlio import _ReferenceAttribute, _ChildTheoryElementList


class NestedNameTheory(NameTheory):
    name_theory = _ReferenceAttribute('name_theory_id',
                                      cls=NameTheory)
    _children = _ChildTheoryElementList('NestedName')
