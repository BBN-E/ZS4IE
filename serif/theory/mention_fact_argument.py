from serif.theory.fact_argument import FactArgument
from serif.theory.mention import Mention
from serif.xmlio import _ReferenceAttribute


class MentionFactArgument(FactArgument):
    mention = _ReferenceAttribute('mention_id',
                                  cls=Mention)
