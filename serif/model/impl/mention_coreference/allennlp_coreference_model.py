import logging

from allennlp.predictors.predictor import Predictor

from serif.model.mention_coref_model import MentionCoreferenceModel

logger = logging.getLogger(__name__)

DUMMY_ENTITY_TYPE = "ALLENNLP_MENTION"


class AllenNLPCoreferenceModel(MentionCoreferenceModel):

    def __init__(self, model, **kwargs):
        super(AllenNLPCoreferenceModel, self).__init__(**kwargs)
        # self.predictor = Predictor.from_path(Path(model))
        self.model = model

    def load_model(self):
        self.predictor = Predictor.from_path(self.model)

    def unload_model(self):
        del self.predictor
        self.predictor = None

    @staticmethod
    def build_token_index_maps(serif_doc):
        index = 0
        index_to_token = list()
        token_idx_to_sent_no = dict()
        tokenized_full_text = list()
        for sentence in serif_doc.sentences or ():
            sent_no = sentence.sent_no
            for token in sentence.token_sequence or ():
                token_idx_to_sent_no[index] = sent_no
                index_to_token.append(token)
                tokenized_full_text.append(token.text)
                index += 1
        return index_to_token, token_idx_to_sent_no, tokenized_full_text

    def add_entities_to_document(self, serif_doc):
        results = []

        index_to_token, token_idx_to_sent_no, tokenized_full_text = self.build_token_index_maps(serif_doc)
        doc_tokens = tokenized_full_text

        # result fields: top_spans, antecedent_indices, predicted_antecedents, document, clusters
        logger.info("Length doc_tokens = {}".format(str(len(doc_tokens))))
        try:
            result = self.predictor.predict_tokenized(doc_tokens)
        except Exception as e:
            logger.info("Exception occurred: {}".format(e))
            logger.info("AllenNLP crashed on document {}, empty results!".format(serif_doc.docid))
            return results

        formatted_clusters = list()
        for cluster in result["clusters"]:
            formatted_cluster = list()
            for span in cluster:
                span = tuple(span)
                start_token_idx_full, end_token_idx_full = span
                start_sent_no = token_idx_to_sent_no[start_token_idx_full]
                end_sent_no = token_idx_to_sent_no[end_token_idx_full]
                if start_sent_no != end_sent_no:
                    continue
                start_token = index_to_token[start_token_idx_full]
                end_token = index_to_token[end_token_idx_full]
                formatted_cluster.append((start_sent_no, start_token, end_token))
            if len(formatted_cluster) > 1:
                formatted_clusters.append(formatted_cluster)
        return MentionCoreferenceModel.resolve_clustering_result(serif_doc, formatted_clusters, DUMMY_ENTITY_TYPE,
                                                                 "NONE", type(self).__name__)


if __name__ == "__main__":
    import argparse
    import serifxml3

    logger.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument('input_serifxml')
    parser.add_argument('output_serifxml')
    args = parser.parse_args()

    model = AllenNLPCoreferenceModel(
        "/nfs/raid88/u10/users/hqiu_ad/data/models/allennlp/coref-spanbert-large-2020.02.27.tar.gz", argparse=args)
    serifdoc = serifxml3.Document(args.input_serifxml)
    serifdoc.add_new_entity_set()
    model.process_document(serifdoc)
    serifdoc.save(args.output_serifxml)
