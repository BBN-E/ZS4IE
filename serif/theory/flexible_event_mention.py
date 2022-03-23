from serif.theory.serif_theory import SerifTheory
from serif.xmlio import _ChildTheoryElementList, _SimpleAttribute


class FlexibleEventMention(SerifTheory):
    args = _ChildTheoryElementList('FlexibleEventMentionArg')
    event_type = _SimpleAttribute(is_required=True)
    modality = _SimpleAttribute(is_required=False, attr_name='Modality')
    number = _SimpleAttribute(is_required=False, attr_name='Number')
    population = _SimpleAttribute(is_required=False, attr_name='Population')
    population1 = _SimpleAttribute(is_required=False, attr_name='Population1')
    population2 = _SimpleAttribute(is_required=False, attr_name='Population2')
    reason = _SimpleAttribute(is_required=False, attr_name='Reason')
    violence = _SimpleAttribute(is_required=False, attr_name='Violence')
