import io, typing
from serif.model.document_model import DocumentModel
from serif.theory.document import Document


class JavaDocumentModel(DocumentModel):
    def __init__(self, **kwargs):
        super(JavaDocumentModel, self).__init__(**kwargs)


