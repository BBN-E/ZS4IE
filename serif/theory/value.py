import re

from serif.theory.serif_theory import SerifTheory
from serif.theory.value_mention import ValueMention
from serif.xmlio import _SimpleAttribute, _ReferenceAttribute


class Value(SerifTheory):
    # todo: should value_mention_ref be renamed to value_mention_id???
    value_mention = _ReferenceAttribute('value_mention_ref',
                                        cls=ValueMention)
    value_type = _SimpleAttribute(attr_name='type', is_required=True)
    timex_val = _SimpleAttribute()
    timex_anchor_val = _SimpleAttribute()
    timex_anchor_dir = _SimpleAttribute()
    timex_set = _SimpleAttribute()
    timex_mod = _SimpleAttribute()
    timex_non_specific = _SimpleAttribute()

    specific_year_re = re.compile('^([12][0-9][0-9][0-9])$')
    specific_sub_year_re = re.compile('^([12][0-9][0-9][0-9])-.*')

    def is_specific_date(self):
        if self.timex_val:
            return (Value.specific_year_re.match(self.timex_val)
                    or Value.specific_sub_year_re.match(self.timex_val))
        else:
            return False
