from serif.theory.serif_theory import SerifTheory
from serif.xmlio import _SimpleAttribute
from serif.theory.enumerated_type import Trend

class EventMentionType(SerifTheory):
    score = _SimpleAttribute(float, default=1.0)
    event_type = _SimpleAttribute(is_required=True)
    magnitude = _SimpleAttribute(float, is_required=False)
    trend = _SimpleAttribute(Trend, is_required=False)