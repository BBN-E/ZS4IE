from serif.theory.serif_offset_theory import SerifOffsetTheory
from serif.theory.token import Token
from serif.xmlio import _ReferenceAttribute


class NPChunk(SerifOffsetTheory):
    start_token = _ReferenceAttribute('start_token', cls=Token,
                                      is_required=True)
    end_token = _ReferenceAttribute('end_token', cls=Token,
                                    is_required=True)
