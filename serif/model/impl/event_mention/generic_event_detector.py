import re
import enum
from serif.model.event_mention_model import EventMentionModel
from serif.theory.enumerated_type import MentionType


class CandidateGenerationMethod(enum.Enum):
    PARSE_TREE = enum.auto()
    POSTAG_FROM_TOKEN = enum.auto()

def preorder_visit(root_synnode, all_event_mention_synnode_candidates):
    if root_synnode is None:
        return
    tag = root_synnode.tag
    if root_synnode.is_preterminal and (
            tag.startswith("VB") or tag.startswith("VV") or tag.startswith("VP") or re.match(r"NNS?",
                                                                                             tag) is not None):
        all_event_mention_synnode_candidates.add(root_synnode)
    for child in root_synnode:
        preorder_visit(child, all_event_mention_synnode_candidates)

class GenericEventDetector(EventMentionModel):
    def __init__(self,**kwargs):
        super(GenericEventDetector, self).__init__(**kwargs)
        self.candidate_generation_method = CandidateGenerationMethod[kwargs.get("candidate_generation_method","PARSE_TREE")]
        self.candidate_cannot_overlap_name_pron = kwargs.get("candidate_cannot_overlap_name_pron", True)

    def add_event_mentions_to_sentence(self, serif_sentence):
        if self.candidate_generation_method == CandidateGenerationMethod.PARSE_TREE:
            if serif_sentence.parse is None:
                return []
            name_or_pron_on_token = [False for _ in range(len(serif_sentence.token_sequence))]
            if self.candidate_cannot_overlap_name_pron:
                for mention in serif_sentence.mention_set:
                    if mention.mention_type in {MentionType.name, MentionType.pron} or mention.resolve_entity_type_from_entity_set().lower() != "undet":
                        start_token = mention.start_token
                        end_token = mention.end_token
                        start_token_idx = start_token.index()
                        end_token_idx = end_token.index()
                        for idx in range(start_token_idx,end_token_idx + 1):
                            name_or_pron_on_token[idx] = True
            all_event_mention_synnode_candidates = set()
            preorder_visit(serif_sentence.parse.root, all_event_mention_synnode_candidates)
            if self.candidate_cannot_overlap_name_pron:
                filtered_all_event_mention_synnode_candidates = set()
                for syn_node in all_event_mention_synnode_candidates:
                    start_token = syn_node.start_token
                    start_token_idx = start_token.index()
                    end_token = syn_node.end_token
                    end_token_idx = end_token.index()
                    is_good_syn_node = True
                    for idx in range(start_token_idx,end_token_idx+1):
                        if name_or_pron_on_token[idx] is True:
                            is_good_syn_node = False
                            break
                    if is_good_syn_node:
                        filtered_all_event_mention_synnode_candidates.add(syn_node)
                all_event_mention_synnode_candidates = filtered_all_event_mention_synnode_candidates
            ret = []
            for synnode in all_event_mention_synnode_candidates:
                ret.extend(EventMentionModel.add_new_event_mention(serif_sentence.event_mention_set, "Event", synnode.start_token,synnode.end_token, score=0.2, model=type(self).__name__))

        else:
            raise NotImplementedError(self.candidate_generation_method)