import logging

logger = logging.getLogger(__name__)
from serif.model.impl.a2t_adapter.utils import modify_or_add_event_mention,modify_or_add_mention

def convert_marked_text_into_plain_text_and_markings(marked_text):
    original_text = ""
    spans = []
    assert marked_text.count("[[") == marked_text.count("]]")
    current_ptr = 0
    while current_ptr < len(marked_text):
        if marked_text[current_ptr] == "[" and current_ptr + 1 < len(marked_text) and marked_text[
            current_ptr + 1] == "[":
            mover = current_ptr + 2
            while mover < len(marked_text) - 1:
                if marked_text[mover] == "]" and marked_text[mover + 1] == "]":
                    break
                mover += 1
            current_trunk = marked_text[current_ptr + 2:mover]
            trunk_original_text, span_type, span_tag = current_trunk.split("|")
            spans.append({"original_text": trunk_original_text, "span_type": span_type, "span_tag": span_tag,
                          "start_char": len(original_text),
                          "end_char": len(original_text) + len(trunk_original_text) - 1})
            original_text += trunk_original_text
            current_ptr = mover + 1
        else:
            original_text += marked_text[current_ptr]
        current_ptr += 1
    return original_text, spans


def add_spans_into_serifxml(serif_doc, spans):
    if len(spans) > 0:
        start_char_to_token = dict()
        end_char_to_token = dict()
        for sentence in serif_doc.sentences:
            for token in sentence.token_sequence:
                # In arabic, some char offset may contains multiple tokens. we need to find the maximum span here
                if token.start_char not in start_char_to_token:
                    start_char_to_token[token.start_char] = token
                end_char_to_token[token.end_char] = token
        for span in spans:
            span_type = span["span_type"]
            span_tag = span["span_tag"]
            start_char = span["start_char"]
            end_char = span["end_char"]
            if start_char not in start_char_to_token or end_char not in end_char_to_token:
                logger.warning("Cannot process span {} due to missing token".format(span))
                continue
            start_token = start_char_to_token[start_char]
            end_token = end_char_to_token[end_char]
            if start_token.sentence != end_token.sentence:
                logger.warning("Cannot process cross sentence span {}".format(span))
                continue
            serif_sentence = start_token.sentence
            if span_type == "Mention":
                if serif_sentence.mention_set is None:
                    serif_sentence.add_new_mention_set()
                modify_or_add_mention(serif_sentence, start_token, end_token, span_tag, 1.0,[[span_tag, "Human annotated", 1.0]])
            elif span_type == "EventMention":
                if serif_sentence.event_mention_set is None:
                    serif_sentence.add_new_event_mention_set()
                modify_or_add_event_mention(serif_sentence, start_token, end_token, span_tag,1.0,[[span_tag, "Human annotated", 1.0]])
            else:
                logger.warning("Cannot handle span type {}".format(span_type))

def event_arg_sentence_to_marking(serif_event_mention, serif_mention):
    serif_sentence = serif_event_mention.sentence
    em_start_char = serif_event_mention.start_char
    em_end_char = serif_event_mention.end_char
    m_start_char = serif_mention.start_char
    m_end_char = serif_mention.end_char
    ret = ""
    for idx, c in enumerate(serif_sentence.get_original_text_substring(serif_sentence.start_char,serif_sentence.end_char)):
        current_char_idx = serif_sentence.start_char + idx
        if current_char_idx == em_start_char:
            ret += "[["
        if current_char_idx == m_start_char:
            ret += "[["
        ret += c
        if current_char_idx == em_end_char:
            ret += "|EventMention|{}]]".format(serif_event_mention.event_type)
        if current_char_idx == m_end_char:
            ret += "|Mention|{}]]".format(serif_mention.entity_type)
    return ret

if __name__ == "__main__":
    text_txt = "[[John Smith|Mention|Person]], a great man, [[died|EventMention|Death]] in [[Florida|Mention|GPE]]."
