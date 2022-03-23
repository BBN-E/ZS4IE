import logging
from abc import abstractmethod

from serif.model.document_model import DocumentModel

logger = logging.getLogger(__name__)


class ValueModel(DocumentModel):

    def __init__(self, **kwargs):
        super(ValueModel, self).__init__(**kwargs)

    @abstractmethod
    def add_new_values_to_document(self, serif_doc):
        pass

    @staticmethod
    def add_new_value(value_set, value_mention, value_type, timex_string, *, timex_anchor_val=None,
                      timex_anchor_dir=None, timex_set=None, timex_mod=None, timex_non_specific=None):
        # build necessary structure
        new_value = value_set.add_new_value(value_mention, value_type, timex_string)
        new_value.timex_anchor_val = timex_anchor_val
        new_value.timex_anchor_dir = timex_anchor_dir
        new_value.timex_set = timex_set
        new_value.timex_mod = timex_mod
        new_value.timex_non_specific = timex_non_specific
        return [new_value]

    def process_document(self, serif_doc):
        value_set = serif_doc.value_set
        if value_set is None:
            value_set = serif_doc.add_new_value_set()
            ''':type: ValueSet'''
        self.add_new_values_to_document(serif_doc)
