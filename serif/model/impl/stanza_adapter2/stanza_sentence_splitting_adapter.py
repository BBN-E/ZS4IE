import logging

from serif.model.impl.stanza_adapter2.utils import get_offsets_for_token
from serif.model.sentence_splitter_model import SentenceSplitterModel

logger = logging.getLogger(__name__)


def stanza_sentence_splitter_adder(current_end_char, stanza_doc, serif_doc, region, original_text, vocab_cls):
    ret = list()
    for stanza_sentence in stanza_doc.sentences:
        start_offset, end_offset = get_offsets_for_token(vocab_cls, stanza_sentence, region.text,
                                                         current_end_char + 1)
        current_end_char = end_offset
        sentence_start = region.start_char + start_offset
        sentence_end = region.start_char + end_offset
        sentence_text = region.text[sentence_start:sentence_end + 1]
        if len(sentence_text.strip()) != 0:
            ret.extend(SentenceSplitterModel.add_new_sentence(serif_doc.sentences, region, sentence_start,
                                                              sentence_end))
            # Attaching stanza_sentence into serif_sentence
            serif_sentence = ret[-1]
            if hasattr(serif_sentence, "aux") is False:
                serif_sentence.aux = dict()
            serif_sentence.aux["stanza_sentence"] = stanza_sentence

    current_end_char += 1
    return current_end_char, ret
