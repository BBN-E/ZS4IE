import logging
from serif.model.mention_model import MentionModel

logger = logging.getLogger(__name__)

class NounPhraseMentionModelNERDeduplication(MentionModel):

    def __init__(self, **kwargs):
        super(NounPhraseMentionModelNERDeduplication, self).__init__(**kwargs)

    def add_mentions_to_sentence(self, sentence):
        raise NotImplementedError("You shouldn't call this endpoint.")

    def process_document(self, serif_doc):
        # Assuming pron mention detector(parse tree based) and NER(model based) has run
        # We'd create NP chunk that 1) not overlap with them 2) if "John Smith" and "John Smith, a great business man" both
        # Are NP, only keep "John Smith"

        for serif_sentence in serif_doc.sentences:
            if serif_sentence.mention_set is None:
                serif_sentence.add_new_mention_set()
            if serif_sentence.parse is None:
                logger.warning("No parse for sentence {}, skipping NounPhraseMentionModel".
                               format(serif_sentence.id))
                continue
            token_is_existing_mention = [False for _ in range(len(serif_sentence.token_sequence or ()))]
            for mention in serif_sentence.mention_set:
                start_token = mention.start_token
                end_token = mention.end_token
                start_token_idx = start_token.index()
                end_token_idx = end_token.index()
                for idx in range(start_token_idx, end_token_idx+1):
                    token_is_existing_mention[idx] = True
            nodes = serif_sentence.parse.get_nodes_matching_tags(["NP"])
            candidate_synnodes = set()
            for node in nodes:
                start_token = node.start_token
                end_token = node.end_token
                start_token_idx = start_token.index()
                end_token_idx = end_token.index()
                is_good_candidate = True
                for idx in range(start_token_idx,end_token_idx+1):
                    if token_is_existing_mention[idx] is True:
                        is_good_candidate = False
                        break
                if is_good_candidate:
                    candidate_synnodes.add(node)
            # Find minimal spans
            token_to_candate_synnodes = dict()
            for node in candidate_synnodes:
                start_token = node.start_token
                end_token = node.end_token
                start_token_idx = start_token.index()
                end_token_idx = end_token.index()
                for idx in range(start_token_idx,end_token_idx+1):
                    token_to_candate_synnodes.setdefault(serif_sentence.token_sequence[idx],set()).add(node)
            node_to_resolved_node = dict()
            for node in candidate_synnodes:
                tokens = node.tokens
                start_token_idx = tokens[0].index()
                end_token_idx = tokens[-1].index()
                candidates = set()
                for token in node.tokens:
                    for another_node in token_to_candate_synnodes.get(token,()):
                        another_node_tokens = another_node.tokens
                        another_node_start_token_idx = another_node_tokens[0].index()
                        another_node_end_token_idx = another_node_tokens[-1].index()
                        if start_token_idx >= another_node_start_token_idx and end_token_idx <= another_node_end_token_idx:
                            candidates.add(another_node)
                selected_candadate = sorted(list(candidates), key=lambda x:len(x.tokens))[0]
                node_to_resolved_node[node] = selected_candadate
            pending_added = set(node_to_resolved_node.values())
            for node in pending_added:
                MentionModel.add_new_mention(serif_sentence.mention_set, 'UNDET', 'DESC', node.start_token, node.end_token, model=type(self).__name__)
