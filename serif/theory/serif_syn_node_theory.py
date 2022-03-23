from serif.theory.serif_sequence_theory import SerifSequenceTheory
from serif.util.head_finder import *


class SerifSynNodeTheory(SerifSequenceTheory):
    @property
    def parent(self):
        from serif.theory.syn_node import SynNode
        """The parent syntactic node (or None for the root node)"""
        owner = self.owner
        if isinstance(owner, SynNode):
            return owner
        else:
            return None

    @property
    def parse(self):
        """The Parse object that contains this SynNode"""
        from serif.theory.syn_node import SynNode
        owner = self.owner
        if isinstance(owner, SynNode):
            return owner.parse
        else:
            return owner

    @property
    def sent_no(self):
        return self.parse.sent_no

    @property
    def right_siblings(self):
        """ A list of siblings to the right of this node, if any exist"""
        if self.parent:
            siblings = [x for x in self.parent]
            index = siblings.index(self)
            return siblings[index + 1:]
        else:
            return []

    @property
    def tokens(self):
        """The list of tokens covered by this SynNode"""
        tok_seq = list(self.parse.token_sequence)
        s = tok_seq.index(self.start_token)
        e = tok_seq.index(self.end_token)
        return tok_seq[s:e + 1]

    @property
    def is_terminal(self):
        """Is this SynNode a terminal?"""
        return len(self) == 0

    @property
    def is_preterminal(self):
        """Is this SynNode a preterminal?"""
        return len(self) == 1 and len(self[0]) == 0

    @property
    def preterminals(self):
        """The list of preterminal SynNode descendents of this SynNode"""
        if len(self) == 0:
            raise ValueError('Can not get preterminals of a terminal')
        if len(self) == 1 and len(self[0]) == 0:
            return [self]
        else:
            return sum((c.preterminals for c in self), [])

    @property
    def terminals(self):
        """The list of terminal SynNode descendents of this SynNode"""
        if len(self) == 0:
            return [self]
        else:
            return sum((c.terminals for c in self), [])

    @property
    def text(self):
        """The original text substring covered by this SynNode"""
        return self.get_original_text_substring(
            self.start_token.start_char, self.end_token.end_char)

    def _get_summary(self):
        return repr(self.text)

    @property
    def head(self):
        """The head child of this SynNode"""
        for child in self:
            if child.is_head: return child
        # Report an error if we didn't find a head?
        return None

    @property
    def headword(self):
        """The text of the head terminal of this SynNode"""
        head_terminal = self.head_terminal
        if head_terminal is None: return None
        return head_terminal.text

    @property
    def head_terminal(self):
        """The head terminal of this SynNode"""
        if len(self) == 0:
            return self
        elif self.head is None:
            return None
        else:
            return self.head.head_terminal

    @property
    def head_preterminal(self):
        """The head pre-terminal of this SynNode"""
        if len(self) == 0:
            raise ValueError('Can not get preterminal of a terminal')
        elif len(self) == 1 and len(self[0]) == 0:
            return self
        elif self.head is None:
            return None
        else:
            return self.head.head_preterminal

    @property
    def head_tag(self):
        """The tag of the head terminal of this SynNode"""
        if len(self) == 0:
            return self.tag
        elif self.head is None:
            return None
        else:
            return self.head.head_tag

    @property
    def start_char(self):
        """The start character index of this SynNode's start token"""
        return self.start_token.start_char

    @property
    def end_char(self):
        """The end character index of this SynNode's end token"""
        return self.end_token.end_char

    @property
    def start_edt(self):
        """The start edt character index of this SynNode's start token"""
        return self.start_token.start_edt

    @property
    def end_edt(self):
        """The end edt character index of this SynNode's end token"""
        return self.end_token.end_edt

    @property
    def mention(self):
        """The mention corresponding to this SynNode, or None if there
           is no such mention."""
        # Cache the value in self._mention, since it's nontrivial to
        # look it up.
        if not hasattr(self, '_mention'):
            parse = self.parse
            if parse is None: return None
            sent = parse.owner
            if sent is None: return None
            mention_set = sent.mention_set
            if mention_set is None: return None
            for mention in mention_set:
                if mention.syn_node == self:
                    self._mention = mention
                    break
            else:
                self._mention = None
        return self._mention

    @property
    def value_mention(self):
        """The value mention corresponding to this SynNode, or None if
           there is no such value mention."""
        # Cache the value in self._value_mention, since it's nontrivial to
        # look it up.
        if not hasattr(self, '_value_mention'):
            parse = self.parse
            if parse is None: return None
            sent = parse.owner
            if sent is None: return None
            value_mention_set = sent.value_mention_set
            if value_mention_set is None: return None
            for value_mention in value_mention_set:
                if (value_mention.start_token == self.start_token and
                        value_mention.end_token == self.end_token):
                    self._value_mention = value_mention
                    break
            else:
                self._value_mention = None
        return self._value_mention

    def _treebank_str(self, depth=-1):
        if len(self) == 0: return self.tag
        s = '(%s' % self.tag
        if self.is_head: s += '^'
        if depth == 0 and len(self) > 0:
            s += ' ...'
        else:
            s += ''.join(' %s' % child._treebank_str(depth - 1)
                         for child in self)
        return s + ')'

    def _pprint_treebank_str(self, indent='', width=75):
        # Try putting this tree on one line.
        self_repr = self.__repr__()
        if len(self_repr) + len(indent) < width:
            return "%s%s" % (indent, self_repr)
        # Otherwise, put each child on a separate line.
        s = '%s(%s' % (indent, self.tag)
        if self.is_head: s += '^'
        for child in self:
            s += '\n' + child._pprint_treebank_str(indent + '  ', width)
        return s + ')'

    def pprint(self, depth=-1, hide=(), follow_pointers=True,
               indent='  ', memo=None):
        return self._treebank_str(depth)

    def __repr__(self):
        s = self._treebank_str()
        return s

    def __str__(self):
        return self._pprint_treebank_str()

    def remove_child(self, child):
        """
        Remove a child from this SynNode.  The child's owner will be
        set to None.
        """
        if child not in self._children:
            raise ValueError('remove_child(c): c not a child')
        self._children.remove(child)
        child.owner = None
        return child

    def gorn_address(self):
        """
        Returns a string containing the Gorn address of this node.
        http://en.wikipedia.org/wiki/Gorn_address
        """
        indices = []
        self._gorn_address(indices)
        # _gorn_address will put the node indices in the list in
        # backwards order
        indices.reverse()
        return ".".join(str(idx) for idx in indices)

    def _gorn_address(self, indexList):
        if self.parent is None:
            indexList.append(0)
        else:
            indexList.append(self.parent._children.index(self))
            self.parent._gorn_address(indexList)

    def set_head_rec(self):
        """Recursively go thorugh the SynNode tree and set the is_head
           attribute based on our head rules (ported from CSerif). 
           This will replace any existing head information.
        """
        if self.is_terminal:
            return
        head_index = find_head_index(self)
        for i in range(len(self._children)):
            if i == head_index:
                self._children[i].is_head = True
            else:
                self._children[i].is_head = False
        for child in self._children:
            child.set_head_rec()
