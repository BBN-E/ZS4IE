from serif.theory.fact_argument import FactArgument
from serif.theory.value_mention import ValueMention
from serif.xmlio import _SimpleAttribute, _ReferenceAttribute


class ValueMentionFactArgument(FactArgument):
    is_doc_date = _SimpleAttribute(bool, default=False)
    value_mention = _ReferenceAttribute('value_mention_id',
                                        cls=ValueMention)
