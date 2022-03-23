from serif.theory.fact_argument import FactArgument
from serif.xmlio import _SimpleAttribute


class TextSpanFactArgument(FactArgument):
    start_sentence = _SimpleAttribute(int)
    end_sentence = _SimpleAttribute(int)
    start_token = _SimpleAttribute(int)
    end_token = _SimpleAttribute(int)
