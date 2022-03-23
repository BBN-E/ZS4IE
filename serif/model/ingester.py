from abc import ABC
from abc import abstractmethod

class Ingester(ABC): 
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def ingest(self, filepath):
        pass
