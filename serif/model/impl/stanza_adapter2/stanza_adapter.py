import enum
import logging

import stanza

from serif.model.document_model import DocumentModel
from serif.model.impl.stanza_adapter2.stanza_ner_adapter import stanza_ner_adder
from serif.model.impl.stanza_adapter2.stanza_parser_adapter import stanza_parsing_adder
from serif.model.impl.stanza_adapter2.stanza_sentence_splitting_adapter import stanza_sentence_splitter_adder
from serif.model.impl.stanza_adapter2.stanza_tokenization_adapter import stanza_tokenizer_adder
from serif.model.impl.stanza_adapter2.utils import build_region_to_text_sections_map

logger = logging.getLogger(__name__)


class StanzaStageToAdd(enum.Enum):
    sentence_splitting = enum.auto()
    tokenization = enum.auto()
    parsing = enum.auto()
    ner = enum.auto()
    universal_dependency = enum.auto()


class StanzaAdapter(DocumentModel):
    def __init__(self, lang, stage_to_add, **kwargs):
        super(StanzaAdapter, self).__init__(**kwargs)
        self.lang = lang
        self.stage_to_add = {StanzaStageToAdd[i.strip()] for i in stage_to_add.split(",")}

    def load_model(self):
        self.vocab_cls = stanza.models.tokenization.vocab.Vocab(lang=self.lang)

    def unload_model(self):
        del self.vocab_cls
        self.vocab_cls = None

    def process_document(self, serif_doc):
        if StanzaStageToAdd.sentence_splitting in self.stage_to_add:
            # Sentence splitting
            serif_doc.add_new_sentences()
            region_to_text_sections = build_region_to_text_sections_map(serif_doc)
            for region in serif_doc.regions:
                current_end_char = -1
                for idx, original_text in enumerate(region_to_text_sections[region]):
                    if len(original_text.strip()) == 0:
                        current_end_char += 1
                        continue
                    stanza_doc = region.aux['stanza_docs'][idx]
                    current_end_char, _ = stanza_sentence_splitter_adder(current_end_char, stanza_doc, serif_doc,
                                                                         region,
                                                                         original_text, self.vocab_cls)

        for serif_sentence in serif_doc.sentences:
            if StanzaStageToAdd.tokenization in self.stage_to_add:
                # Tokenization
                stanza_tokenizer_adder(serif_sentence, self.vocab_cls)
            if StanzaStageToAdd.parsing in self.stage_to_add:
                # Parsing
                stanza_parsing_adder(serif_sentence)
            if StanzaStageToAdd.ner in self.stage_to_add:
                # NER
                stanza_ner_adder(serif_sentence)
            if StanzaStageToAdd.universal_dependency in self.stage_to_add:
                # TODO: depparse
                raise NotImplementedError()
