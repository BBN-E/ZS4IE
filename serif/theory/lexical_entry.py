from serif.theory.serif_theory import SerifTheory
from serif.xmlio import _SimpleAttribute, _ReferenceListAttribute


class LexicalEntry(SerifTheory):
    key = _SimpleAttribute()
    category = _SimpleAttribute()
    voweled_string = _SimpleAttribute()
    pos = _SimpleAttribute()
    gloss = _SimpleAttribute()
    analysis = _ReferenceListAttribute('analysis',
                                       cls='LexicalEntry')
