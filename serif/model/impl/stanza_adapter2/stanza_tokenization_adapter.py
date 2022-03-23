import logging

from serif.model.impl.stanza_adapter2.utils import get_offsets_for_token

logger = logging.getLogger(__name__)


def stanza_tokenizer_adder(serif_sentence, vocab_cls):
    token_sequence = serif_sentence.add_new_token_sequence()
    token_sequence.set_score(0.7)
    pos_sequence = serif_sentence.add_new_part_of_speech_sequence()
    pos_sequence.set_score(0.7)
    if "stanza_sentence" not in serif_sentence.aux:
        logger.warning("Cannot find stanza_sentence for {}, skipping!!".format(serif_sentence.text))
        return
    stanza_sentence = serif_sentence.aux["stanza_sentence"]
    last_end = -1
    for stanza_token in stanza_sentence.tokens:
        start_offset, end_offset = get_offsets_for_token(
            vocab_cls, stanza_token, serif_sentence.text, last_end + 1)
        last_end = end_offset
        for stanford_word in stanza_token.words:
            serif_token = token_sequence.add_new_token(
                serif_sentence.start_char + start_offset,
                serif_sentence.start_char + end_offset,
                stanford_word.text,
                stanford_word.lemma)
    for i in range(len(stanza_sentence.tokens)):
        stanford_token = stanza_sentence.tokens[i]
        serif_token = token_sequence[i]
        word = stanford_token.words[-1]
        governor = word.head
        if governor != 0:
            # Substract 1 from governor due to Stanford being 1-indexed
            serif_token.head = token_sequence[governor - 1]
        pos_sequence.add_new_pos(
            serif_token, word.xpos, word.upos,
            word.deprel.split(":")[0])
    return
