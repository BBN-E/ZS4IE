import json

from serif.model.event_mention_model import EventMentionModel
from serif.model.mention_model import MentionModel, MentionType

def modify_or_add_mention(serif_sentence, start_token, end_token, label, confidence, debug_info):
    typed_span_to_mention = dict()
    for mention in serif_sentence.mention_set:
        typed_span_to_mention.setdefault((mention.start_token, mention.end_token, mention.resolve_entity_type_from_entity_set()),set()).add(mention)

    if (start_token, end_token,label) in typed_span_to_mention:
        for mention in typed_span_to_mention[(start_token, end_token,label)]:
            if mention.model == "Ask2Transformers":
                if mention.pattern is None:
                    mention.pattern = json.dumps([])
                existing_debug_info_string = json.loads(mention.pattern)
                existing_debug_info_string.extend(debug_info)
                mention.pattern = json.dumps(existing_debug_info_string)
            else:
                mention.model = "Ask2Transformers"
                mention.mention_type = MentionType.name
                mention.pattern = json.dumps(debug_info)
            mention.confidence = confidence
    else:
        MentionModel.add_new_mention(serif_sentence.mention_set, entity_type=label, mention_type="NAME",
                                 start_token=start_token, end_token=end_token,
                                 confidence=confidence, model="Ask2Transformers",
                                 pattern=json.dumps(list(debug_info)))

def modify_or_add_event_mention(serif_sentence, start_token, end_token, label, score, debug_info):
    typed_span_to_ems = dict()
    for event_mention in serif_sentence.event_mention_set:
        typed_span_to_ems.setdefault((event_mention.start_token, event_mention.end_token, event_mention.event_type),set()).add(event_mention)
    if (start_token, end_token, label) in typed_span_to_ems:
        for event_mention in typed_span_to_ems[(start_token,end_token,label)]:
            if event_mention.model == "Ask2Transformers":
                if event_mention.pattern_id is None:
                    event_mention.pattern_id = json.dumps([])
                existing_debug_info_string = json.loads(event_mention.pattern_id)
                existing_debug_info_string.extend(debug_info)
                event_mention.pattern_id = json.dumps(existing_debug_info_string)
            else:
                event_mention.model = "Ask2Transformers"
                event_mention.pattern_id = json.dumps(debug_info)
            event_mention.score = score
    else:
        EventMentionModel.add_new_event_mention(serif_sentence.event_mention_set, label, start_token,
                                                end_token, score=score, model="Ask2Transformers",
                                                pattern_id=json.dumps(list(debug_info)))


def modify_serifxml_from_unary_markings(serif_doc,json_doc):
    for sentence in json_doc['sentences']:
        serif_sentence = serif_doc.sentences[sentence['sent_no']]
        for mention_span in sentence['unary_markings']['mentions']:
            if serif_sentence.mention_set is None:
                serif_sentence.add_new_mention_set()
            start_token = serif_sentence.token_sequence[mention_span['start']]
            end_token = serif_sentence.token_sequence[mention_span['end']]
            span_tag = mention_span['entity_type']
            modify_or_add_mention(serif_sentence, start_token, end_token, span_tag, 1.0,
                                  [[span_tag, "Human annotated", 1.0]])
        for event_mention_span in sentence['unary_markings']['event_mentions']:
            if serif_sentence.event_mention_set is None:
                serif_sentence.add_new_event_mention_set()
            start_token = serif_sentence.token_sequence[event_mention_span['start']]
            end_token = serif_sentence.token_sequence[event_mention_span['end']]
            span_tag = event_mention_span['event_type']
            modify_or_add_event_mention(serif_sentence, start_token, end_token, span_tag, 1.0,
                                        [[span_tag, "Human annotated", 1.0]])