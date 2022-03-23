import re

from serif.theory.serif_theory import SerifTheory
from serif.theory.syn_node import SynNode
from serif.xmlio import ET


class SerifParseTheory(SerifTheory):
    def _init_from_etree(self, etree, owner):
        SerifTheory._init_from_etree(self, etree, owner)
        if self.root is None:
            if self._treebank_string is None:
                raise ValueError('Parse requires SynNode or TreebankString')
            else:
                self._parse_treebank_string()
        assert self.root is not None or len(self.token_sequence) == 0

    indent = 0

    def toxml(self, etree=None, **options):
        indent = options.get('indent')
        if indent is not None: options['indent'] += '  '

        if etree is None:
            etree = ET.Element(self.__class__.__theory_name__)
        else:
            assert etree.tag == self.__class__.__theory_name__

        parse_format = options.get('parse_format', 'treebank').lower()
        # Add all attributes; but skip _treebank_string, and also skip
        # _root if we're serializing the tree as a treebank string.
        for name, attr in self._auto_attribs:
            if name == '_treebank_string': continue
            if name == 'root' and parse_format == 'treebank': continue
            attr.serialize(etree, self, **options)
        # Serialize the tree as a treebank string (if requested)
        if parse_format == 'treebank':
            treebank_str = ET.Element('TreebankString')
            treebank_str.attrib['node_id_method'] = 'DFS'
            if self.root is None:
                treebank_str.text = '(X^ -empty-)'
            else:
                treebank_str.text = self.root._treebank_str()
            del etree[:]  # discard old treebank string.
            etree.append(treebank_str)
        # [xx] should there be an else clause here?

        # Indentation...
        if len(etree) > 0 and indent is not None:
            etree.text = '\n' + indent + '  '
            for child in etree[:-1]:
                child.tail = '\n' + indent + '  '
            etree[-1].tail = '\n' + indent
        if indent is not None: options['indent'] = indent
        etree.tail = '\n'
        return etree

    # to do -- handle is_head!
    _TB_TOKEN = re.compile('|'.join([
        '\((?P<start>[^\s\^]+)(?P<headmark>\^?)', '(?P<end>\))',
        '\s+', '(?P<token>[^\(\)\s]+)']))

    def _parse_treebank_string(self):
        token_sequence = self.token_sequence
        # Special case: if there's no token sequence, then we can't
        # define a parse (since the parse points into the token seq)
        if len(token_sequence) == 0:
            if (self._treebank_string != '(X^ -empty-)' and
                    self._treebank_string != '(FRAG^)'):
                print(('Warning: discarding treebank string %r because '
                       'no token sequence is defined' % self._treebank_string))
            self.root = None
            del self._treebank_string
            return

        token_index = 0
        stack = [self]
        dfs_count = 0
        for piece in self._TB_TOKEN.finditer(self._treebank_string):
            if piece.group('start') or piece.group('token'):
                if token_index >= len(token_sequence):
                    # print `self._treebank_string`
                    # print `token_sequence`
                    raise ValueError(
                        "Number of terminals in parse string is "
                        "greater than the number of tokens in the "
                        "token sequence (%d)" % len(token_sequence))
                tag = piece.group('start') or piece.group('token')
                syn_node = SynNode(tag=tag, owner=stack[-1])
                syn_node.start_token = token_sequence[token_index]
                syn_node.end_token = None  # filled in later.
                syn_node.is_head = piece.group('headmark') == '^'
                syn_node.id = '%s.%s' % (self.id, dfs_count)
                dfs_count += 1
                self.document.register_id(syn_node)
                if piece.group('start'):
                    stack.append(syn_node)
                else:
                    syn_node.end_token = self.token_sequence[token_index]
                    syn_node.is_head = True
                    token_index += 1
                    stack[-1]._children.append(syn_node)
            elif piece.group('end'):
                assert len(stack) > 1
                assert token_index > 0
                completed = stack.pop()
                completed.end_token = self.token_sequence[token_index - 1]
                if stack[-1] is self:
                    assert self.root is None
                    self.root = completed
                else:
                    stack[-1]._children.append(completed)
        assert token_index == len(self.token_sequence), (
            self.token_sequence, token_index, self._treebank_string)
        assert len(stack) == 1
        self._treebank_string = None

    @property
    def sent_no(self):
        if self.owner:
            return self.owner.sent_no
        else:
            return None

    def get_covering_syn_node(self, start_token, end_token, tags):
        """Returns the lowest SynNode that covers the tokens, restricted
           by tag prefix
        """
        tok_seq = list(self.token_sequence)
        start = tok_seq.index(start_token)
        end = tok_seq.index(end_token)
        smallest_node = None
        root = self.root
        smallest_node = self._get_covering_node_rec(
            root, smallest_node, start, end, tok_seq, tags)
        return smallest_node
    
    def _get_covering_node_rec(self, node, smallest_node, start, end, tok_seq, tags):
        s = tok_seq.index(node.start_token)
        e = tok_seq.index(node.end_token)

        if len(tags) == 0:
            # Allow any tag
            if s <= start and e >= end:
                smallest_node = node
        else:
            # Restrict tags
            if any(node.tag.startswith(t) for t in tags) and s <= start and e >= end:
                smallest_node = node

        # Prefer child NPs
        for child in node:
            if not child.is_terminal: # to avoid treating words that begin with "NP" as tags
                smallest_node = self._get_covering_node_rec(
                    child, smallest_node, start, end, tok_seq, tags)

        return smallest_node

    def get_nodes_matching_tags(self, tags):
        """Returns all SynNodes in the parse which match a 
           tag prefix
        """
        matches = []
        if self.root is not None:
            matches = self._get_nodes_matching_tags_rec(
                self.root, tags, matches)
        return matches
    
    def _get_nodes_matching_tags_rec(self, node, tags, matches):
        if any(node.tag.startswith(t) for t in tags):
            matches.append(node)
        for child in node:
            if child.is_terminal:
                continue
            matches = self._get_nodes_matching_tags_rec(
                child, tags, matches)
        return matches
        
    def add_heads(self):
        """Recursively go thorugh the parse tree and set the SynNode
           is_head attribute based on our head rules (ported from 
           CSerif). This will replace any existing head information.
        """ 
        self.root.is_head = True
        self.root.set_head_rec()
