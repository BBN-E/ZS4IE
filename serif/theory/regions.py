from serif.theory.serif_sequence_theory import SerifSequenceTheory
from serif.xmlio import _ChildTheoryElementList


class Regions(SerifSequenceTheory):
    _children = _ChildTheoryElementList('Region')

    def add_region(self, region):
        self._children.append(region)

    def get_regions(self):
        return self._children
