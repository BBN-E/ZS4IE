from serif.theory.serif_theory import SerifTheory
from serif.xmlio import _SimpleAttribute, _ChildTheoryElementList


class Fact(SerifTheory):
    start_sentence = _SimpleAttribute(int)
    end_sentence = _SimpleAttribute(int)
    start_token = _SimpleAttribute(int)
    end_token = _SimpleAttribute(int)
    fact_type = _SimpleAttribute()
    pattern_id = _SimpleAttribute()
    score_group = _SimpleAttribute(int)
    score = _SimpleAttribute(float)

    mention_fact_arguments = _ChildTheoryElementList('MentionFactArgument')
    value_mention_fact_arguments = _ChildTheoryElementList('ValueMentionFactArgument')
    text_span_fact_arguments = _ChildTheoryElementList('TextSpanFactArgument')
    string_fact_arguments = _ChildTheoryElementList('StringFactArgument')
