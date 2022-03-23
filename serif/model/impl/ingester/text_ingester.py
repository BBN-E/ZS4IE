import os, re

from serif import Document
from serif.model.ingester import Ingester

class TextIngester(Ingester):
    def __init__(self, lang,
                 metadata_file_path=None,
                 mtdp_to_serifxml_preprocessing_metadata_file_path=None, **kwargs):
        super(TextIngester, self).__init__(**kwargs)
        self.language = lang

        self.metadata_file_path = metadata_file_path
        if self.metadata_file_path is not None:
            self.docid_to_dct = self.extract_docid_to_dct_from_metadata_file(metadata_file_path)

        self.mtdp_to_serifxml_preprocessing_metadata_file_path = mtdp_to_serifxml_preprocessing_metadata_file_path
        if self.mtdp_to_serifxml_preprocessing_metadata_file_path is not None:
            self.docid_to_dct_start_end = self.extract_docid_to_dct_start_end_from_mtdp_metadata_file(mtdp_to_serifxml_preprocessing_metadata_file_path)

    def ingest(self, filepath):
        docid = self.get_docid_from_filename(filepath)
        doc = Document.from_text(filepath, self.language, docid)

        if self.metadata_file_path is not None and docid in self.docid_to_dct:
            dct = self.docid_to_dct[docid]

            doc.document_time_start, doc.document_time_end = self.normalize_dct(dct)
        elif self.mtdp_to_serifxml_preprocessing_metadata_file_path is not None and docid in self.docid_to_dct_start_end:
            doc.document_time_start = self.docid_to_dct_start_end[docid][0]
            doc.document_time_end = self.docid_to_dct_start_end[docid][1]

        return [doc]
    
    def get_docid_from_filename(self, filepath):
        basename = os.path.basename(filepath)
        if basename.endswith(".txt"):
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

    def extract_docid_to_dct_start_end_from_mtdp_metadata_file(self, mtdp_metadata_file):

        lines = [l.strip().split('\t') for l in open(mtdp_metadata_file, 'r').readlines()]
        docid_to_dct_filepath = {l[0]: l[1] for l in lines}

        docid_to_dct_start_end = dict()
        for docid, dct_filepath in docid_to_dct_filepath.items():

            with open(dct_filepath, "r") as f:
                metadata_for_docid = [l.strip() for l in f.readlines()]

            assert docid == metadata_for_docid[0]

            dct_start = metadata_for_docid[1]
            dct_end = metadata_for_docid[2]

            docid_to_dct_start_end[docid] = (dct_start, dct_end)

        return docid_to_dct_start_end