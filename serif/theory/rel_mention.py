from serif.theory.enumerated_type import Tense, Modality
from serif.theory.mention import Mention
from serif.theory.serif_theory import SerifTheory
from serif.theory.value_mention import ValueMention
from serif.xmlio import _SimpleAttribute, _ReferenceAttribute


class RelMention(SerifTheory):
    pattern = _SimpleAttribute()
    score = _SimpleAttribute(float, default=1.0)
    confidence = _SimpleAttribute(float, default=1.0)
    type = _SimpleAttribute(is_required=True)
    raw_type = _SimpleAttribute()
    tense = _SimpleAttribute(Tense, is_required=True)
    modality = _SimpleAttribute(Modality, is_required=True)
    left_mention = _ReferenceAttribute('left_mention_id', cls=Mention)
    right_mention = _ReferenceAttribute('right_mention_id', cls=Mention)
    time_arg = _ReferenceAttribute('time_arg_id', cls=ValueMention)
    time_arg_role = _SimpleAttribute()
    time_arg_score = _SimpleAttribute(float, default=0.0)
    model = _SimpleAttribute(is_required=False)
