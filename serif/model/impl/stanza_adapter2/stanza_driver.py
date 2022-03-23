import logging

import stanza
import torch

from serif.model.document_model import DocumentModel
from serif.model.impl.stanza_adapter2.utils import build_region_to_text_sections_map

logger = logging.getLogger(__name__)


class StanzaDriver(DocumentModel):
    def load_model(self):
        self.pipeline = \
            stanza.Pipeline(  # This now will do everything. sentence splitting, tokenization, parsing, ner
                lang=self.lang,
                model_dir=self.model_dir,
                package='default',
                use_gpu=True)
        self.vocab_cls = stanza.models.tokenization.vocab.Vocab(lang=self.lang)

    def unload_model(self):
        if self.pipeline is not None:
            del self.pipeline
        del self.vocab_cls
        self.pipeline = None
        self.vocab_cls = None
        torch.cuda.empty_cache()

    def __init__(self, lang, model_dir, **kwargs):
        super(StanzaDriver, self).__init__(**kwargs)
        self.lang = lang
        self.model_dir = model_dir

    def process_document(self, serif_doc):
        # Assume there's no sentence splitting at the beginning
        # Ideally we'll need to implement the following
        # Three ingestion mode 1) raw text 2) sentence split, no tokenized 3) tokenized
        # Also, for 1) and 2), before we send text to stanza, we may need to apply prefilter

        # raw text mode
        # We still want to split on line breaks for saving computing resource
        region_to_text_sections = build_region_to_text_sections_map(serif_doc)
        for region, text_sections in region_to_text_sections.items():
            for original_text in text_sections:
                if len(original_text.strip()) == 0:

                    if hasattr(region, "aux") is False:
                        region.aux = dict()
                    region.aux.setdefault("stanza_docs", list()).append(None)
                    continue
                stanza_doc = self.pipeline(original_text)
                if hasattr(region, "aux") is False:
                    region.aux = dict()
                region.aux.setdefault("stanza_docs", list()).append(stanza_doc)
