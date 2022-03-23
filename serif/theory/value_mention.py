from serif.theory.serif_value_mention_theory import SerifValueMentionTheory
from serif.theory.token import Token
from serif.xmlio import _SimpleAttribute, _ReferenceAttribute


class ValueMention(SerifValueMentionTheory):
    value_type = _SimpleAttribute(is_required=True)
    start_token = _ReferenceAttribute('start_token', cls=Token,
                                      is_required=True)
    end_token = _ReferenceAttribute('end_token', cls=Token,
                                    is_required=True)
    sent_no = _SimpleAttribute(int, default=None)
