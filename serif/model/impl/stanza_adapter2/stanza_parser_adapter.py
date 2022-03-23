import logging

from serif.model.parser_model import ParserModel

logger = logging.getLogger(__name__)


class DuckParseModel(ParserModel):
    def __init__(self, **kwargs):
        super(ParserModel, self).__init__(**kwargs)
        self.add_heads = True

    def add_parse_to_sentence(self, serif_sentence):
        raise NotImplementedError


def stanza_parsing_adder(serif_sentence):
    original_parse_model = DuckParseModel()
    if "stanza_sentence" not in serif_sentence.aux:
        logger.warning("Cannot find stanza_sentence for {}, skipping!!".format(serif_sentence.text))
        original_parse_model.add_new_parse(serif_sentence, "(S ())")
        return
    stanza_sentence = serif_sentence.aux["stanza_sentence"]
    # It seems that we may have a better solution here https://github.com/stanfordnlp/stanza/blob/dev/stanza/models/constituency/parse_tree.py
    stanza_parser_string = format(stanza_sentence.constituency)
    original_parse_model.add_new_parse(serif_sentence, stanza_parser_string)

