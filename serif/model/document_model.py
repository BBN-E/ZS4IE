import logging
import traceback
from abc import abstractmethod

from serif.model.base_model import BaseModel
from serif.theory.document import Document

logger = logging.getLogger(__name__)


class DocumentModel(BaseModel):
    def __init__(self, **kwargs):
        super(DocumentModel, self).__init__(**kwargs)

    @abstractmethod
    def process_document(self, serif_doc):
        pass

    def begin_document(self, serif_doc):
        pass

    def apply(self, serif_docs):
        """
        :type serif_docs: list(Document)
        :rtype list(Document)
        """
        resolved_docs = list()
        for idx, document in enumerate(serif_docs):
            logger.info(
                "({}/{}) Applying {} to {}".format(idx + 1, len(serif_docs), type(self).__name__, document.docid))
            resolved_docs.append(self.apply_to_document(document))
        return resolved_docs

    def apply_to_document(self, serif_doc):
        """
        :type serif_doc: Document
        :rtype Document
        """
        changed_document_theory = serif_doc
        try:
            self.begin_document(serif_doc)
            ret_doc = self.process_document(changed_document_theory)
            if isinstance(ret_doc, Document) and ret_doc is not changed_document_theory:
                changed_document_theory = ret_doc
            return changed_document_theory
        except Exception as e:
            logger.exception("doc: {} model: {}".format(serif_doc.docid, type(self).__name__))
            logger.exception(traceback.format_exc())
            if self.argparse.PRODUCTION_MODE is False:
                raise e
            return changed_document_theory
        # DONT USE FINALLY HERE AS IT IS EATING THE EXCEPTION


