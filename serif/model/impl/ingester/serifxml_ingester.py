import os, serifxml3

from serif.model.ingester import Ingester

class SerifxmlIngester(Ingester):
    def __init__(self, **kwargs):
        super(SerifxmlIngester, self).__init__(**kwargs)

    def ingest(self, filepath):
        return [serifxml3.Document(filepath)]
    
