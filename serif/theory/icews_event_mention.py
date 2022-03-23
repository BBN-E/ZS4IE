from serif.theory.proposition import Proposition
from serif.theory.serif_theory import SerifTheory
from serif.theory.value_mention import ValueMention
from serif.xmlio import _SimpleAttribute, _ChildTheoryElementList, _ReferenceAttribute, _ReferenceListAttribute


class ICEWSEventMention(SerifTheory):
    participants = _ChildTheoryElementList('ICEWSEventParticipant')
    event_code = _SimpleAttribute(is_required=True)
    event_tense = _SimpleAttribute(is_required=True)
    pattern_id = _SimpleAttribute(is_required=True)
    time_value_mention = _ReferenceAttribute('time_value_mention_id',
                                             cls=ValueMention,
                                             is_required=False)
    propositions = _ReferenceListAttribute('proposition_ids', cls=Proposition)
    original_event_id = _SimpleAttribute(is_required=False)
    is_reciprocal = _SimpleAttribute(bool, is_required=False)
