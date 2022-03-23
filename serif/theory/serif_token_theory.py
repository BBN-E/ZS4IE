from serif.theory.serif_offset_theory import SerifOffsetTheory


class SerifTokenTheory(SerifOffsetTheory):
    def _init_from_etree(self, etree, owner):
        SerifOffsetTheory._init_from_etree(self, etree, owner)
        # If the text is not specified, it defaults to the original
        # text substring.
        if self.text is None:
            self.text = self.original_text_substring

    @property
    def syn_node(self):
        """The terminal SynNode corresponding to this Token, or None
           if the parse is not available."""
        # Cache the value in self._syn_node, since it's nontrivial to
        # look it up.
        from serif.theory.sentence import Sentence
        if not hasattr(self, '_syn_node'):
            if self.owner is None: return None
            sent = self.owner_with_type(Sentence)
            if sent is None: return None
            parse = sent.parse
            if parse is None: return None
            self._syn_node = self._find_syn_node(parse.root)
        return self._syn_node

    def _find_syn_node(self, syn_node):
        if len(syn_node) == 0:
            # @hqiu. There's a chance that max token length is small that not every token appears in the parse tree
            if syn_node.start_token == syn_node.end_token == self:
                return syn_node
            else:
                return None
        elif len(syn_node) == 1:
            return self._find_syn_node(syn_node[0])
        else:
            for child in syn_node:
                if ((child.start_char <= self.start_char) and
                        (self.end_char <= child.end_char)):
                    return self._find_syn_node(child)
            return None  # should never happen

    def index(self):
        """Returns the index of this token in its token sequence.
        """
        return self.owner.index(self)

    def token_sequence(self):
        """Returns this Token's TokenSequence"""
        return self.owner

    def preceeds(self, other):
        """Returns True if this Token preceeds the given Token in the 
           Document. Assumes both Tokens are from the same Document.
        """
        if (self.token_sequence().sentence().sent_no <
            other.token_sequence().sentence().sent_no):
            return True
        if (self.is_in_same_sentence_as(other) and
            self.index() < other.index()):
            return True
        return False
        
    def preceeds_or_is(self, other):
        """Returns True if this Token is the same object as the given Token 
           or preceeds it in the Document. Assumes both Tokens are from 
           the same Document.
        """
        return self == other or self.preceeds(other)

    def follows(self, other):
        """Returns True if this Token is after the given Token in the 
           Document. Assumes both Tokens are from the same document.
        """
        if (self.token_sequence().sentence().sent_no >
            other.token_sequence().sentence().sent_no):
            return True
        if (self.is_in_same_sentence_as(other) and
            self.index() > other.index()):
            return True
        return False

    def follows_or_is(self, other):
        """Returns True if this Token is the same object as the given Token 
           or is after it in the Document. Assumes both Tokens are from 
           the same Document.
        """
        return self == other or self.follows(other)

    def is_in_same_sentence_as(self, other):
        """Returns True if both Tokens are from the same sentence"""
        return (self.token_sequence().sentence() == 
                other.token_sequence().sentence())

    def previous_token(self):
        """Returns the token right before this Token in its Sentence, 
           or None if this Token is the first one in the Sentence
        """
        if self.index() == 0:
            return None
        return self.token_sequence()[self.index() - 1]

    def next_token(self):
        """Returns the token after this one in its Sentence or 
           None if this Token is the last one in the Sentence
        """
        if self.index() == len(self.token_sequence()) - 1:
            return None
        return self.token_sequence()[self.index() + 1]
    
    def shift(self, relative_index):
        """Returns the Token at the specified index relative to this one
           if available. For example supplying a value of -2 will
           return the Token two before this one if possible.
        """
        index = self.index() + relative_index
        if index >= 0 and index < len(self.token_sequence()):
            return self.token_sequence()[index]
        else:
            return None

    def __repr__(self):
        return '<%s: %r>' % (self.__class__.__theory_name__, self.text)
