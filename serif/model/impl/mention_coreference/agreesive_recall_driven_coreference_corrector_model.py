from serif.model.mention_coref_model import MentionCoreferenceModel


class AgreesiveRecallDrivenCoreferenceCorrectorModel(MentionCoreferenceModel):
    def __init__(self, **kwargs):
        super(AgreesiveRecallDrivenCoreferenceCorrectorModel, self).__init__(**kwargs)

    def add_entities_to_document(self, serif_doc):
        mention_to_representative_mention = dict()
        representative_mention_to_mentions = dict()
        for serif_sentence in serif_doc.sentences:
            token_idx_to_mentions = dict()
            mention_to_token_length = dict()
            for serif_mention in serif_sentence.mention_set or ():
                if serif_mention.start_token is not None and serif_mention.end_token is not None:
                    start_token_idx = serif_mention.start_token.index()
                    end_token_idx = serif_mention.end_token.index()
                else:
                    start_token_idx = serif_mention.syn_node.start_token.index()
                    end_token_idx = serif_mention.syn_node.end_token.index()
                mention_to_token_length[serif_mention] = end_token_idx - start_token_idx + 1
                for token_idx in range(start_token_idx, end_token_idx+1):
                    token_idx_to_mentions.setdefault(token_idx, set()).add(serif_mention)
            for serif_mention in serif_sentence.mention_set or ():
                if serif_mention.start_token is not None and serif_mention.end_token is not None:
                    start_token_idx = serif_mention.start_token.index()
                    end_token_idx = serif_mention.end_token.index()
                else:
                    start_token_idx = serif_mention.syn_node.start_token.index()
                    end_token_idx = serif_mention.syn_node.end_token.index()
                longest_mention_token_length = end_token_idx - start_token_idx + 1
                longest_mention = serif_mention
                for token_idx in range(start_token_idx, end_token_idx + 1):
                    for candidate_serif_mention in token_idx_to_mentions[token_idx]:
                        if mention_to_token_length[candidate_serif_mention] > longest_mention_token_length:
                            longest_mention = candidate_serif_mention
                            longest_mention_token_length = mention_to_token_length[candidate_serif_mention]

                mention_to_representative_mention[serif_mention] = longest_mention
                representative_mention_to_mentions.setdefault(longest_mention,set()).add(serif_mention)


        bk_old_entity_set = list(serif_doc.entity_set._children) # We need this because we need redo the entity type resolution
        serif_doc.entity_set._children.clear()
        added_entity = set()
        ret = list()
        for old_entity in bk_old_entity_set:
            aggregated_mention_set = set()
            for mention in old_entity.mentions:
                aggregated_mention_set.add(mention)
                representative_mention = mention_to_representative_mention[mention]
                aggregated_mention_set.update(representative_mention_to_mentions[representative_mention])
            frozen_aggregated_mention_set = frozenset(aggregated_mention_set)
            if frozen_aggregated_mention_set not in added_entity:
                ret.extend(MentionCoreferenceModel.add_new_entity(
                    entity_set = serif_doc.entity_set,
                    mention_group = list(frozen_aggregated_mention_set),
                    entity_type = "UNDET", # We want to trigger the entity type resolution algorithm
                    entity_subtype = old_entity.entity_subtype,
                    is_generic = old_entity.is_generic,
                    canonical_name = old_entity.canonical_name,
                    entity_guid = old_entity.entity_guid,
                    confidence = old_entity.confidence,
                    mention_confidences = old_entity.mention_confidences,
                    cross_document_instance_id = old_entity.cross_document_instance_id,
                    model = old_entity.model
                ))
                added_entity.add(frozen_aggregated_mention_set)
        return ret