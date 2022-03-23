from serif.theory.name import Name
from serif.xmlio import _ReferenceAttribute


class NestedName(Name):
    parent = _ReferenceAttribute('parent', cls=Name,
                                 is_required=True)
