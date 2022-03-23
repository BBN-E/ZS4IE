import logging

logger = logging.getLogger(__name__)


def get_offsets_for_token(vocab_cls, stanford_token, sentence, start_search):
    start = None
    token_pos = 0
    sentence_pos = start_search

    def stanford_normalize_char(current_char):
        """Stanford's normalizer is designed to work on token and strips leading space.
        Adding an 'X' to avoid that to work on single character.

        See https://github.com/stanfordnlp/stanza/blob/master/stanza/models/tokenize/vocab.py#L29
        """
        return vocab_cls.normalize_token('X' + current_char)[1:]

    while True:
        if token_pos >= len(stanford_token.text):
            break

        current_char = sentence[sentence_pos]

        # A tokenized stanford_token can contain space inside like ": )".
        # To cope with that we only skip leading spaces
        if start is None and current_char.isspace():
            sentence_pos += 1
        # stanford_token.text is normalized so that TAB becomes ' ':
        # we need to keep that in mind when comparing characters
        elif stanford_token.text[token_pos].isspace() or sentence[sentence_pos].isspace():
            while token_pos < len(stanford_token.text) and stanford_token.text[token_pos].isspace():
                token_pos += 1
            while sentence_pos < len(sentence) and sentence[sentence_pos].isspace():
                sentence_pos += 1
        elif stanford_normalize_char(current_char) != stanford_token.text[token_pos]:
            if current_char == " " and stanford_token.text[
                token_pos] == "_":  # this is OK, we did a substitution in get_tokenized_sentence_text()
                pass
            else:
                logger.critical("Character mismatch in tokenizer! %s (ord=%d) != %s (ord=%d)" % (current_char,
                                                                                                 ord(current_char),
                                                                                                 stanford_token.text[
                                                                                                     token_pos],
                                                                                                 ord(
                                                                                                     stanford_token.text[
                                                                                                         token_pos])))
            logger.critical("Sentence: {}".format(sentence))
            raise AssertionError()
        else:
            if start is None:
                start = sentence_pos
            sentence_pos += 1
            token_pos += 1
    return start, sentence_pos - 1


def build_region_to_text_sections_map(serif_doc):
    region_to_text_sections = dict()
    for region in serif_doc.regions:
        text_sections = region.text.splitlines()
        region_to_text_sections[region] = text_sections
    return region_to_text_sections
