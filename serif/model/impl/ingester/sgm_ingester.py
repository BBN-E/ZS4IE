import os, re

from serif import Document
from serif.model.ingester import Ingester

class SgmIngester(Ingester):
    def __init__(self, lang, metadata_file_path=None, **kwargs):
        super(SgmIngester, self).__init__(**kwargs)
        self.language = lang
        self.metadata_file_path = metadata_file_path
        if self.metadata_file_path is not None:
            self.docid_to_dct = self.extract_docid_to_dct_from_metadata_file(metadata_file_path)

    def ingest(self, filepath):
        doc = Document.from_sgm(filepath, self.language)
        docid = self.get_docid_from_filename(filepath)
        if self.docid_to_dct is not None and docid in self.docid_to_dct:
            dct = self.docid_to_dct[docid]
            doc.document_time_start, doc.document_time_end = self.normalize_dct(dct)
        return [doc]

    def get_docid_from_filename(self, filepath):
        basename = os.path.basename(filepath)
        if basename.endswith(".sgm"):
            basename = basename[0:-4]
        return basename
    
    def extract_docid_to_dct_from_metadata_file(self, metadata_file_path):
        lines = [l.strip().split('\t') for l in open(metadata_file_path, 'r').readlines()]
        docid_to_dct = {l[0]: l[2] for l in lines}
        return docid_to_dct

    def normalize_dct(self, dct="20200405"):
        '''dct of format YYYYMMDD'''

        m = re.fullmatch(pattern=r"([12]\d\d\d)(\d\d)(\d\d)", string=dct)
        start = "{}-{}-{}T00:00:00".format(m.group(1), m.group(2), m.group(3))
        end = "{}-{}-{}T23:59:59".format(m.group(1), m.group(2), m.group(3))
        return start, end

