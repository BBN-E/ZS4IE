import logging
import traceback

import benepar

from serif.model.parser_model import ParserModel

logger = logging.getLogger(__name__)


class BeneparParser(ParserModel):
    def __init__(self, model, **kwargs):
        super(BeneparParser, self).__init__(**kwargs)
        self.model = model
        self.max_tokens = 100000
        if "max_tokens" in kwargs:
            self.max_tokens = int(kwargs["max_tokens"])

    def load_model(self):
        self.parser = benepar.Parser(self.model)

    def unload_model(self):
        del self.parser
        self.parser = None
        benepar_version = benepar.__version__
        benepar_version_second_digit = int(benepar_version.split(".")[1])
        if int(benepar_version.split(".")[0]) == 0 and benepar_version_second_digit < 2:
            import tensorflow as tf
            tf.keras.backend.clear_session()

    def fix_token_for_benepar(self, text):
        text = text.strip()
        text = text.replace(" ", "_")
        # Benepar doesn't like it when we have a bracket with other
        # text in the token. Remove the brackets, leave the text if 
        # possible.
        brackets = ["(", ")", "[", "]", "{", "}"]
        for bracket in brackets:
            if len(text) > 1 and text.find(bracket) != -1:
                text = text.replace(bracket, "")
            if len(text) == 0:
                text = bracket
        return text

    def get_tokens(self, sentence):
        token_texts = []
        for token in sentence.token_sequence._children:
            token_texts.append(self.fix_token_for_benepar(token.text))
        return token_texts

    def add_parse_to_sentence(self, sentence):
        if len(sentence.token_sequence) > self.max_tokens:
            logger.info(f"Skipping Benepar on long sentence: ({len(sentence.token_sequence)})")
            return []
        token_texts = self.get_tokens(sentence)
        try:
            tree = self.parser.parse(token_texts)
            treebank_str = tree.pformat()
            return self.add_new_parse(sentence, treebank_str)
        except Exception as e:
            logger.exception(traceback.format_exc())
            return []
