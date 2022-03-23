import logging

from serif.model.mention_model import MentionModel
from serif.model.name_model import NameModel

logger = logging.getLogger(__name__)


class DuckNameModel(NameModel):
    def add_names_to_sentence(self, serif_sentence):
        raise NotImplementedError()

    def maintain_deduplication_set_for_sentence(self, serif_sentence):
        self.name_hash.clear()
        for n in serif_sentence.name_theory:
            self.name_hash.setdefault((n.entity_type, n.start_token, n.end_token), list()).append(n)

class DuckMentionModel(MentionModel):
    def add_mentions_to_sentence(self, sentence):
        raise NotImplementedError()
    def maintain_deduplication_set_for_sentence(self, serif_sentence):
        self.existing_mentions_by_span.clear()
        self.existing_mentions_by_type_and_span.clear()
        for m in serif_sentence.mention_set:
            tokens = m.tokens
            span_key = tokens[0], tokens[-1]
            full_key = m.entity_type, m.mention_type == "NAME", tokens[0], tokens[-1]
            self.existing_mentions_by_span[span_key].append(m)
            self.existing_mentions_by_type_and_span[full_key].append(m)

def stanza_ner_adder(serif_sentence):
    if serif_sentence.name_theory is None:
        serif_sentence.add_new_name_theory()
    if serif_sentence.mention_set is None:
        serif_sentence.add_new_mention_set()
    if "stanza_sentence" not in serif_sentence.aux:
        logger.warning("Cannot find stanza_sentence for {}, skipping!!".format(serif_sentence.text))
    # Init name_model for deduplication
    name_model = DuckNameModel()
    # Init mention_model for deduplication
    mention_model = DuckMentionModel()

    stanza_sentence = serif_sentence.aux["stanza_sentence"]
    stanza_entities = stanza_sentence.entities
    # In this case, assume stanza token idx will match serif token idx
    stanza_token_start_to_stanza_token_idx = dict()
    stanza_token_end_to_stanza_token_idx = dict()
    for token_idx, token in enumerate(stanza_sentence.tokens):
        start_char = token.start_char
        end_char = token.end_char
        stanza_token_start_to_stanza_token_idx.setdefault(start_char, list()).append(token_idx)
        stanza_token_end_to_stanza_token_idx.setdefault(end_char, list()).append(token_idx)

    for stanza_entity in stanza_entities:
        earliest_start_token = min(stanza_token_start_to_stanza_token_idx[stanza_entity.start_char])
        latest_end_token = max(stanza_token_end_to_stanza_token_idx[stanza_entity.end_char])
        serif_start_token = serif_sentence.token_sequence[earliest_start_token]
        serif_end_token = serif_sentence.token_sequence[latest_end_token]
        entity_type = stanza_entity.type
        name_model.add_or_update_name(serif_sentence.name_theory, entity_type, serif_start_token, serif_end_token)
        mention_model.add_or_update_mention(serif_sentence.mention_set, entity_type, "NAME", serif_start_token,
                                     serif_end_token, model="StanzaAdapter")