import logging
from abc import abstractmethod
from collections import defaultdict

from serif.model.document_model import DocumentModel
from serif.model.mention_model import MentionModel
from serif.model.validate import *
from collections import Counter

logger = logging.getLogger(__name__)


class MentionCoreferenceModel(DocumentModel):

    def __init__(self, **kwargs):
        super(MentionCoreferenceModel, self).__init__(**kwargs)
        self.clear_entity_set = False
        if "clear_entity_set" in kwargs:
            self.clear_entity_set = True

    @staticmethod
    def add_new_entity(entity_set, mention_group, *, entity_type="UNDET", entity_subtype=None, is_generic=True,
                       canonical_name=None, entity_guid=None, confidence=None, mention_confidences=None,
                       cross_document_instance_id=None, model=None):
        entities = []
        if entity_type == "UNDET":
            if len(mention_group) > 0:
                entity_types = [m.entity_type for m in mention_group if m.entity_type != 'UNDET']
                if len(entity_types) > 0:
                    entity_type = MentionCoreferenceModel.get_best_type(entity_types)
        if entity_subtype is None:
            if len(mention_group) > 0:
                entity_subtypes = [m.entity_subtype for m in mention_group if m.entity_subtype != 'UNDET']
                if len(entity_subtypes) > 0:
                    count_data = Counter(entity_subtypes)
                    entity_subtype = count_data.most_common(1)[0][0]
        entity = entity_set.add_new_entity(
            mention_group, entity_type, entity_subtype, is_generic)
        entity.canonical_name = canonical_name
        entity.entity_guid = entity_guid
        entity.confidence = confidence
        entity.mention_confidences = mention_confidences
        entity.cross_document_instance_id = cross_document_instance_id
        entity.model = model
        entities.append(entity)
        return entities

    @abstractmethod
    def add_entities_to_document(self, serif_doc):
        pass

    @staticmethod
    def get_best_type(entity_types, sep="."):
        '''determines best entity type on a majority-win basis'''

        if len(entity_types) == 1:
            return list(entity_types)[0]

        entity_types = [t.split(sep) for t in sorted(list(entity_types))]

        # determine base type
        basetype_to_count = defaultdict(int)
        for t in entity_types:
            basetype_to_count[t[0]] += 1
        majority_basetype = max(list(basetype_to_count.keys()), key=lambda x: basetype_to_count[x])

        # determine subtype
        subtype_candidates = [t for t in entity_types if len(t) > 1 and t[0] == majority_basetype]
        if len(subtype_candidates) == 0:
            return majority_basetype
        subtype_to_count = defaultdict(int)
        for t in subtype_candidates:
            subtype_to_count[t[1]] += 1
        majority_subtype = max(list(subtype_to_count.keys()), key=lambda x: subtype_to_count[x])
        # if there's a tie between subtypes, back off
        if list(subtype_to_count.values()).count(subtype_to_count[majority_subtype]) > 1:
            return majority_basetype

        # determine subsubtype
        subsubtype_candidates = [t for t in entity_types if len(t) == 3 and t[1] == majority_subtype]
        if len(subsubtype_candidates) == 0:
            return sep.join([majority_basetype, majority_subtype])
        subsubtype_to_count = defaultdict(int)
        for t in subsubtype_candidates:
            subsubtype_to_count[t[2]] += 1
        majority_subsubtype = max(list(subsubtype_to_count.keys()), key=lambda x: subsubtype_to_count[x])
        # if there's a tie between subsubtypes, back off
        if list(subsubtype_to_count.values()).count(subsubtype_to_count[majority_subtype]) > 1:
            return sep.join([majority_basetype, majority_subtype])

        return sep.join([majority_basetype, majority_subtype, majority_subsubtype])

    @staticmethod
    def resolve_clustering_result(serif_doc, cluster_to_mention_spans, DUMMY_ENTITY_TYPE, DUMMY_MENTION_TYPE, model):
        sentence_to_existing_mentions = dict()
        cluster_to_mentions = dict()
        results = list()
        for sentence in serif_doc.sentences:
            sent_no = sentence.sent_no
            if sentence.mention_set is None:
                sentence.add_new_mention_set()
            for mention in sentence.mention_set:
                sentence_to_existing_mentions.setdefault(sent_no, dict()).setdefault(
                    (mention.tokens[0].index(), mention.tokens[-1].index()), set()).add(mention)
        exact_hit_mention_spans_in_cluster = set()
        # For this pass, if 1) Say [A B C] is in cluster X, and 2) [B] is in cluster Y, we only have mention A [B] C. We don't want case 1) to fuzzy align to mention B, but instead we should create new mention
        for cluster_idx, cluster in enumerate(cluster_to_mention_spans):
            for cluster_sent_no, cluster_start_token, cluster_end_token in cluster:
                cluster_start_token_idx = cluster_start_token.index()
                cluster_end_token_idx = cluster_end_token.index()
                exact_hit_mention_spans_in_cluster.add(
                    (cluster_sent_no, cluster_start_token_idx, cluster_end_token_idx))
        # This pass, we decide mention alignment
        for cluster_idx, cluster in enumerate(cluster_to_mention_spans):
            for cluster_sent_no, cluster_start_token, cluster_end_token in cluster:
                cluster_start_token_idx = cluster_start_token.index()
                cluster_end_token_idx = cluster_end_token.index()
                cluster_token_idx_set = set(range(cluster_start_token_idx, cluster_end_token_idx + 1))
                serif_sentence = serif_doc.sentences[cluster_sent_no]
                candidate_mentions = set()
                # Exact hit
                candidate_mentions.update(sentence_to_existing_mentions.get(cluster_sent_no, dict()).get(
                    (cluster_start_token_idx, cluster_end_token_idx), set()))
                if len(candidate_mentions) < 1:
                    # Second pass, same sentence, uwcoref span is smaller than sentence mention span, and sentence mention span is not in other cluster
                    for (start_token_idx, end_token_idx), mentions in sentence_to_existing_mentions.get(cluster_sent_no,
                                                                                                        dict()).items():
                        candidate_token_idx_set = set(range(start_token_idx, end_token_idx + 1))
                        token_idx_intersect = set(candidate_token_idx_set).intersection(cluster_token_idx_set)
                        token_idx_union = set(candidate_token_idx_set).union(cluster_token_idx_set)
                        # {0 1} [2 3]
                        if len(token_idx_intersect) < 1:
                            continue
                        # {0 [1 2} 3]
                        if len(cluster_token_idx_set - token_idx_intersect) > 0 and len(
                                candidate_token_idx_set - token_idx_intersect) > 0:
                            continue
                        if (cluster_sent_no, start_token_idx,
                            end_token_idx) not in exact_hit_mention_spans_in_cluster and len(token_idx_intersect) / len(
                            token_idx_union) > 0.85:
                            # Fuzzy align. https://en.wikipedia.org/wiki/Jaccard_index
                            candidate_mentions.update(mentions)
                if len(candidate_mentions) < 1:
                    logger.info("Adding new Mention {}".format(
                        serif_doc.get_original_text_substring(cluster_start_token.start_char,
                                                              cluster_end_token.end_char)))
                    new_mentions = MentionModel.add_new_mention(serif_sentence.mention_set, DUMMY_ENTITY_TYPE,
                                                                DUMMY_MENTION_TYPE,
                                                                cluster_start_token, cluster_end_token, model=model)
                    sentence_to_existing_mentions.setdefault(cluster_sent_no, dict()).setdefault(
                        (cluster_start_token_idx, cluster_end_token_idx), set()).update(new_mentions)
                    candidate_mentions.update(new_mentions)
                if cluster_idx not in cluster_to_mentions:
                    cluster_to_mentions[cluster_idx] = []
                cluster_to_mentions[cluster_idx].extend(candidate_mentions)
        for cluster_idx, mention_list in cluster_to_mentions.items():
            if len(mention_list) > 0:
                logger.debug("Cluster {}: {}".format(cluster_idx, " || ".join(
                    m.get_original_text_substring(m.tokens[0].start_char, m.tokens[-1].end_char) for m in
                    mention_list)))
                results.extend(MentionCoreferenceModel.add_new_entity(serif_doc.entity_set, mention_list,
                                                                      model=model))

    def process_document(self, serif_doc):
        validate_doc_sentences(serif_doc)
        entity_set = serif_doc.entity_set
        if entity_set is None or self.clear_entity_set:
            entity_set = serif_doc.add_new_entity_set()
        self.add_entities_to_document(serif_doc)
