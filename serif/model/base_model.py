from abc import ABC, abstractmethod


class BaseModel(ABC):
    def __init__(self, **kwargs):
        self.argparse = kwargs.get("argparse", None)

    def process(self, serif_doc):
        raise NotImplementedError("This method is depreciated. Please implement corpus_model or document_model")

    def load_model(self):
        pass

    def unload_model(self):
        pass

    @abstractmethod
    def apply(self, serif_docs):
        """
        :type serif_docs: list(Document)
        :rtype list(Document)
        """
        pass
