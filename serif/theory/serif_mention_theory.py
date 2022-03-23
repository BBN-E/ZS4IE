from serif.theory.enumerated_type import MentionType
from serif.theory.serif_theory import SerifTheory


class SerifMentionTheory(SerifTheory):
    @property
    def child_mention_list(self):
        """A list of the children of this mention.  This list contains
        child_mention (if defined), plus the chain of next_mentions
        starting at child_mention.
        """
        if self.child_mention is None: return []
        child_mentions = [self.child_mention]
        while child_mentions[-1].next_mention is not None:
            child_mentions.append(child_mentions[-1].next_mention)
        return child_mentions

    @property
    def text(self):
        """The text content of this mention."""
        if self.syn_node is not None:
            return self.syn_node.text
        else:
            sent = self.document.sentences[self.sent_no]
            return sent.token_sequence.get_original_text_substring(self.start_char, self.end_char)

    @property
    def tokens(self):
        """The tokens contained in this mention's SynNode."""
        if self.syn_node is not None:
            return self.syn_node.tokens
        else:
            sent = self.document.sentences[self.sent_no]
            return sent.token_sequence[self.start_token.index(): self.end_token.index() + 1]

    @property
    def start_char(self):
        """The start character index of this Mention's SynNode
           or start Token if there is no SynNode"""
        if self.syn_node is not None:
            return self.syn_node.start_token.start_char
        return self.start_token.start_char

    @property
    def end_char(self):
        """The end character index of this Mention's SynNode
           or end Token if there is no SynNOde"""
        if self.syn_node is not None:
            return self.syn_node.end_token.end_char
        return self.end_token.end_char

    @property
    def start_edt(self):
        if self.syn_node is not None:
            return self.syn_node.start_token.start_edt
        return self.start_token.start_edt

    @property
    def end_edt(self):
        if self.syn_node is not None:
            return self.syn_node.end_token.end_edt
        return self.end_token.end_edt

    def _get_summary(self):
        if self.syn_node is None:
            return None
        else:
            return self.syn_node._get_summary()

    @property
    def sent_no(self):
        if self.syn_node is not None:
            return self.syn_node.sent_no
        elif self.start_token.syn_node is not None and self.start_token.syn_node.sent_no is not None:
            return self.start_token.syn_node.sent_no
        else:
            return self.start_token.sentence.sent_no

    @property
    def head(self):
        """Replicates the behavior of Java's head() function.
           For name Mentions, returns the node that matches the
           bottom-most child. For appostives and list Mentions, returns
           the node of the first Mention. Otherwise return the
           head preterminal.
        """
        if self.syn_node is None:
            return None
        if self.mention_type == MentionType.name:
            if self.child_mention is not None:
                m = self.child_mention
                while m.child_mention is not None:
                    m = m.child_mention
                return m.syn_node
            else:
                return self.syn_node
        elif self.mention_type == MentionType.pron:
            return self.syn_node
        elif (self.mention_type == MentionType.appo or
              self.mention_type == MentionType.list):
            return self.child_mention.syn_node
        else:
            return self.syn_node.head_preterminal

    @property
    def atomic_head(self):
        """Replicates the behavior of SERIF's getAtomicHead.  If this Mention
           is a name, it returns the head preterminal's parent. Otherwise it
           returns the head's preterminal.
        """
        if self.syn_node is None:
            return None
        if self.mention_type == MentionType.name and self.syn_node.head_preterminal is not None:
            return self.syn_node.head_preterminal.parent
        else:
            return self.syn_node.head_preterminal

    @property
    def premod_text(self):
        e_min = self.syn_node.start_token.start_char
        h_min = self.head.start_token.start_char
        if h_min > e_min:
            return self.get_original_text_substring(e_min, h_min - 1)
        else:
            return ''

    @property
    def postmod_text(self):
        h_max = self.head.end_token.end_char
        e_max = self.syn_node.end_token.end_char
        if e_max > h_max:
            return self.get_original_text_substring(h_max + 1, e_max)
        else:
            return ''

    def is_name(self):
        """Returns true if this Mention is of type name or if it is of
           type none and its parent is_name() is true"""
        return (self.mention_type == MentionType.name or
                (self.parent_mention is not None and
                 self.parent_mention.is_name()))

    def is_base_name(self):
        """Returns true if this Mention is a name Mention and has no children"""
        return self.is_name() and self.child_mention is None

    def entity(self):
        """Returns the entity that contains this Mention"""
        return self.document.entity_by_mention(self)

    def index_in_sentence(self):
        """Returns the index of this Mention in its sentence's Mention list"""
        sent = self.document.sentences[self.sent_no]
        count = 0
        for m in sent.mention_set:
            if m == self:
                return count
            count += 1
        return -1

    def resolve_entity_type_from_entity_set(serif_mention):
        if serif_mention.entity_type.lower() != "undet":
            return serif_mention.entity_type
        start_token = serif_mention.start_token
        end_token = serif_mention.end_token
        start_token_idx = start_token.index()
        end_token_idx = end_token.index()

        serif_doc = serif_mention.document
        serif_sentence = serif_mention.sentence

        overlapping_mentions = set()
        overlapping_mentions.add(serif_mention)

        for mention in serif_sentence.mention_set:
            another_mention_start_token = mention.start_token
            another_mention_end_token = mention.end_token
            another_mention_start_token_idx = another_mention_start_token.index()
            another_mention_end_token_idx = another_mention_end_token.index()
            if another_mention_start_token_idx <= start_token_idx and another_mention_end_token_idx >= end_token_idx:
                overlapping_mentions.add(mention)
        entity_type_str_to_cnt = dict()

        for entity in serif_doc.entity_set or ():
            is_mention_in_entity = serif_mention in entity.mentions
            if is_mention_in_entity:
                if entity.entity_type.lower() != "undet":
                    # We want to normalize the entity type count in case we need to go through the corefered mention for resolving
                    entity_type_str_to_cnt[entity.entity_type] = entity_type_str_to_cnt.get(entity.entity_type,
                                                                                            0) + len(entity.mentions)
                else:
                    for mention in entity.mentions:
                        if mention.entity_type.lower() != "undet":
                            entity_type_str_to_cnt[mention.entity_type] = entity_type_str_to_cnt.get(
                                mention.entity_type, 0) + 1

        resolved_entity_type = "UNDET"
        for entity_type, cnt in sorted(entity_type_str_to_cnt.items(), key=lambda x: x[1], reverse=True):
            if entity_type.lower() != "undet":
                resolved_entity_type = entity_type
                break
        return resolved_entity_type