import enum

from serif.model.parser_model import ParserModel


class POSTagGetter(enum.IntEnum):
    XPOS = 1
    UPOS = 2
    UNKNOWN = 3


class AllTokenFlattenParser(ParserModel):
    """
    This is a fallback strategy for languages that we cannot get constituency parsing but we somehow need a parse tree structure for compatible purpose
    """

    def __init__(self, postag_attr_getter_str, fallback_pos_tag, **kwargs):
        super(AllTokenFlattenParser, self).__init__(**kwargs)
        if postag_attr_getter_str.lower() in {"pos", "xpos"}:
            self.postag_attr_getter = POSTagGetter.XPOS
        elif postag_attr_getter_str.lower() == "upos":
            self.postag_attr_getter = POSTagGetter.UPOS
        elif postag_attr_getter_str.lower() == "unknown":
            self.postag_attr_getter = POSTagGetter.UNKNOWN
        else:
            raise ValueError(
                "{} is not supported yet. Please add them into pos.py, then token.py, then change get_parse_info method below.")
        self.skip_sentence_has_parsing = False
        if "skip_sentence_has_parsing" in kwargs and kwargs["skip_sentence_has_parsing"].lower() == "true":
            self.skip_sentence_has_parsing = True
        self.fallback_pos_tag = fallback_pos_tag

    def add_parse_to_sentence(self, serif_sentence):
        if serif_sentence.parse is not None and self.skip_sentence_has_parsing is True:
            return []
        token_postag_tuples = list()
        l_subs = {
            "(": "-LRB-",
            ")": "-RRB-",
            " ": "_"
        }
        for token in serif_sentence.token_sequence or ():
            current_postag = self.fallback_pos_tag
            if self.postag_attr_getter == POSTagGetter.XPOS:
                xpos = token.xpos
                if xpos is not None:
                    current_postag = xpos
            elif self.postag_attr_getter == POSTagGetter.UPOS:
                upos = token.upos
                if upos is not None:
                    current_postag = upos
            elif self.postag_attr_getter == POSTagGetter.UNKNOWN:
                pass
            else:
                raise NotImplementedError
            t = ""
            for c in token.text:
                t += l_subs.get(c, c)
            token_postag_tuples.append((current_postag, t))
        return self.add_new_parse(serif_sentence,
                                  "(ROOT (S {}))".format(" ".join("({} {})".format(x[0], x[1]) for x in token_postag_tuples)))
