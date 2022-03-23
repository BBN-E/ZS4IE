from serif.theory.serif_offset_theory import SerifOffsetTheory
from serif.theory.token import Token
from serif.xmlio import _SimpleAttribute, _ReferenceAttribute


class Name(SerifOffsetTheory):
    entity_type = _SimpleAttribute(is_required=True)
    start_token = _ReferenceAttribute('start_token', cls=Token,
                                      is_required=True)
    end_token = _ReferenceAttribute('end_token', cls=Token,
                                    is_required=True)
    transliteration = _SimpleAttribute(is_required=False)
    score = _SimpleAttribute(float, is_required=False)
