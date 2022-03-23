from serif.theory.serif_theory import SerifTheory
from serif.xmlio import _SimpleAttribute


class DefaultCountryActor(SerifTheory):
    actor_db_name = _SimpleAttribute()
    actor_uid = _SimpleAttribute(int)
