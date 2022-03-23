#!/bin/env python
#
# Copyright 2013 by Raytheon BBN Technologies Corp.
# All Rights Reserved.
import logging,enum
from serifxml3 import ActorMention, Document, Entity, EventMention, EventMentionArg, Genericity, ICEWSEventMention, \
    Mention, MentionType, Polarity, PredType, PropStatus, RelMention, Sentence, Tense, Event
from xml.sax.saxutils import escape as escape_xml
import hashlib, os, re, stat, subprocess, textwrap,abc
from collections import defaultdict

logger = logging.getLogger(__name__)

PRUNE_PROP_TREES = True
USE_ORIGINAL_TEXT_FOR_TOKENS = False

# If false, then prune out any entities that aren't connected via
# an edge to anything else.
INCLUDE_DISCONNECTED_ENTITIES_IN_MERGED_GRAPH = True

FORCE_REDRAW_DOT = True

BLANK_PAGE = ''
GUILLEMETS = u'\xab%s\xbb'
MINUS = '&#8722;'

# This is just used for debugging; it should be left false:
SKIP_SENTENCE_PAGES = False

TAGSET = 'penn-treebank'
# TAGSET = 'ancora'

###########################################################################
## Graphviz Configuration
###########################################################################

PROP_EDGE_STYLE = {
    '<ref>': 'color="#880000",fontcolor="#880000"',
    '<sub>': 'color="#008800",fontcolor="#008800"',
    '<obj>': 'color="#000088",fontcolor="#000088"',
    '<head>': 'color="#000000:#000000"',
}

DOT_GRAPH_OPTIONS = '''
ranksep="%(ranksep)s";
nodesep=".1";
rankdir="LR";
node [fontsize="10",tooltip=""];
edge [fontsize="10",tooltip=""];
graph [bgcolor=transparent];
'''

###########################################################################
## HTML Templates
###########################################################################

FRAMES_HTML = r'''
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN"
          "DTD/xhtml1-frameset.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
  <title> SerifXML Viewer </title>
</head>
<frameset cols="20%,80%">
  <frame src="nav.html" name="serifxmlDocNavFrame"
         id="serifxmlDocNavFrame" />
  <frameset rows="1*,1*,25">
    <frame src="blank_page.html" name="serifxmlTextFrame"
           id="serifxmlTextFrame"/>
    <frame src="blank_page.html" name="serifxmlDetailsFrame"
           id="serifxmlDetailsFrame"/>
    <frame src="blank_page.html" name="serifxmlNavFrame"
           id="serifxmlNavFrame" />
  </frameset>
</frameset>
</html>
'''.lstrip()

# Template for HTML pages.  Arguments: title, script, body
HTML_PAGE = '''\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
   "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
  <title>%(title)s</title>
  <link rel="stylesheet" href="serifxml_viewer.css" type="text/css" />
  <script type="text/javascript" src="jquery.js" >
  </script>
  <script type="text/javascript" src="jstree.js"></script>
  <script type="text/javascript" src="serifxml_viewer.js"></script>
  <script type="text/javascript">
    %(script)s
  </script>
</head>
<body class="%(css)s">
%(body)s
</body>
</html>
'''

# Body for the document navigation page.
DOC_NAV_BODY = '''
<h1>SerifXML Viewer</h1>
<div id="doc-nav">
<ul>
%s
</ul>
</div>'''

# Body for the sentence context page.
SENT_CONTEXT_BODY = '''
<a href="#" id="prev-sent">&larr;Prev (p)</a>
<span class="sentno">Sentence %(sent_no)s in
<span class="docid">%(docid)s</span></span>
<a href="#" id="next-sent">(n) Next&rarr;</a>
</div>
'''

# Script for the document text page.  Should these global/shared
# javascript variables be moved to the frameset itself?
DOCUMENT_TEXT_SCRIPT = '''
var selected_tab_id="parse";
var doc_url_prefix="%(doc_url_prefix)s";
$(document).ready(function() {setupTextFrame(); });
'''

# Pane for the sentence details page.
SENTENCE_DETAILS_PANE = '''
  <div id="%(tab_id)s-pane" class="nav-pane">
    <div class="%(tab_id)s">
%(body)s
    </div>
  </div>
'''

DOC_ENTITY_GRAPH = '''
  <div class="doc-entity-graph-wrapper">
    <a class="show-entity-graph" href="#">Show entity graph</a>
    <div class="doc-entity-graph collapsed">
%s
    </div>
  </div>
'''

ZOOMABLE_GRAPH = '''
<div class="zoomable-graph">
[<a href="#" class="graph-zoom-out">Zoom Out</a> |
<a href="#" class="graph-zoom-in">Zoom In</a>]
<div class="graph">
%s
</div>
</div>
'''


###########################################################################
## Parse -> HTML
###########################################################################
def parse_to_html(sentence, highlights=None):
    """
    @param highlights: A dictionary mapping SynNode->css class
    """
    if highlights is None:
        highlights = dict()
    parse = None
    score = float("-inf")
    parses = [st.parse for st in sentence.sentence_theories if st.parse is not None]
    for p in parses:
        if p.score > score:
            parse = p
            score = p.score
    if parse is None or parse.root is None:
        return '<i>No parse is available for this sentence</i>\n'
    s = '<div class="syntree">\n<ul><li>\n'
    s += syn_to_html(parse.root, highlights)
    s += '</li></ul>\n<div class="clear"></div>\n</div>\n'
    return s


def syn_to_html(syn_node, highlights, css_class='svn-root', tagset=None):
    if tagset is None:
        if syn_node.document.language == 'Spanish':
            tagset = 'ancora'
        else:
            tagset = 'penn-treebank'

    assert len(syn_node) != 0

    if tagset == 'ancora':
        if syn_node.tag in ('SP', 'P', 'p'):
            css_class = 'syn-p'
        elif syn_node.tag in ('SN', 'GRUP.NOM', 'n'):
            css_class = 'syn-n'
        elif syn_node.tag in ('GRUP.VERB', 'v'):
            css_class = 'syn-v'
        elif syn_node.tag in ('S', 'SENTENCE'):
            css_class = 'syn-s'
        elif syn_node.tag.startswith('S.F.'):
            css_class = 'syn-s'
        elif syn_node.tag in ('SADV', 'GRUP.ADV', 'r'):
            css_class = 'syn-adv'
        elif syn_node.tag in ('SA', 'S.A', 'GRUP.ADJ', 'a'):
            css_class = 'syn-adj'
        elif syn_node.tag in ('CONJ'):
            css_class = 'syn-conj'
    else:
        if syn_node.tag.startswith('PP'):
            css_class = 'syn-p'
        elif syn_node.tag.startswith('N'):
            css_class = 'syn-n'
        elif syn_node.tag.startswith('V'):
            css_class = 'syn-v'
        elif syn_node.tag.startswith('S'):
            css_class = 'syn-s'

    # Node information
    css = [css_class]
    if len(syn_node) == 1 and len(syn_node[0]) == 0:
        css.append('preterminal')
    if syn_node.is_head:
        css.append('head')
    if syn_node in highlights:
        css.append(highlights[syn_node])
    css = css and (' class="%s"' % ' '.join(css)) or ''
    s = '<h3 title="%s"%s>%s' % (syn_node.tag, css, syn_node.tag)

    mention = syn_node.mention
    if mention is not None:  # and mention.mention_type.value != 'none':
        s += '<div class="info">'
        s += mention.mention_type.value
        if mention.entity_type != 'UNDET':
            s += ': '
            if len(syn_node.text) < 10:
                s += '<br/>'
            etype = mention.entity_type
            # if etype == 'OTH': etype = ''
            if mention.entity_subtype != 'UNDET':
                etype += '.' + mention.entity_subtype
            s += etype
        s += '</div>'
    s += '</h3>'

    # Children
    if len(syn_node) == 1 and len(syn_node[0]) == 0:
        # n.b.: we use the token's text, not its tag.
        s += '<div class="word">%s</div>' % (syn_node[0].text,)
    else:
        s += '<ul>'
        for child in syn_node:
            child_html = syn_to_html(child, highlights, css_class, tagset)
            s += '<li>%s</li>' % (child_html,)
        s += '</ul>'
    return s


###########################################################################
## Graphviz/Dot: graph generation
###########################################################################

_VALID_DOT_ID_RE = re.compile(r'^[a-zA-Z][a-zA-Z0-9\-\_]*$')


def dot_id(v):
    id_attr = getattr(v, 'id', None)
    if id_attr is not None and _VALID_DOT_ID_RE.match(id_attr):
        return id_attr
    else:
        return 'n%s' % id(v)


def escape_dot(s, wrap=False, justify='c', quotes=False):
    # Choose what kind of newline to use (based on justify)
    if justify == 'c':
        newline = '\\n'
    elif justify == 'l':
        newline = newline = '\\l'
    elif justify == 'r':
        newline = newline = '\\r'
    else:
        assert 0, 'bad justify value!'
    # Add quotes if requested
    if quotes:
        s = '"%s"' % s
    # Normalize whitespace
    s = ' '.join(s.split())
    # Wrap if requested
    if wrap:
        s = textwrap.fill(s, 25)
    # Escape characters that have special meaning
    s = escape_xml(s)  # Escape '&', '<', and '>' in a string of data.
    s = re.sub(r'([\"\\|@{}])', r'\\\1', s)
    # Replace newlines
    s = s.replace('\n', newline) + newline
    # That's all!
    return s


def quote_dot(s, justify='l'):
    return escape_dot(s, True, justify, True)


def quote_dot1(s, justify='l'):
    return escape_dot(s, True, justify, False)


def is_boring_prop(prop):
    if not PRUNE_PROP_TREES: return False
    # All verb props are interesting.
    if prop.pred_type in (PredType.verb, PredType.copula):  # @UndefinedVariable
        return False
    # A proposition that doesn't connect anything is boring.
    if len(prop.arguments) == 1:
        return True
    # Name props are always boring
    if prop.pred_type == PredType.name:  # @UndefinedVariable
        return True
    # Everything else is interesting
    return False


def prop_arg_dir(pred_type, arg_role):
    if arg_role == '<ref>' and pred_type != PredType.modifier:  # @UndefinedVariable
        return 'back'
    if arg_role == '<sub>':
        return 'back'
    else:
        return 'forward'


def mention_port(mention):
    return 'm' + hashlib.sha224(mention.text.encode('utf-8')).hexdigest()


def entity_type(entity):
    etype = entity.entity_type
    if entity.entity_subtype != 'UNDET':
        etype += '.%s' % entity.entity_subtype
    return etype


def entity_dot_label(entity):
    etype = entity_type(entity)
    mention_texts = set((m.text, mention_port(m)) for m in entity.mentions)

    mentions = '|'.join('<%s>%s' % (port, quote_dot(text))
                        for (text, port) in mention_texts)
    return '%s|%s' % (etype, mentions)


def entity_dot_label1(entity, mention):
    etype = entity_type(entity)
    mention_texts = set((m, mention_port(m)) for m in entity.mentions)
    s = '<<TABLE BORDER="0" CELLBORDER="1" RULES="ROWS" FRAME="HSIDES" CELLSPACING="0" ><TR><TD>%s</TD></TR>' % etype
    for (m, port) in mention_texts:
        text = m.text
        temp_text = quote_dot1(text).replace("\l", " ").strip()
        atomic_head_text = m.text
        if m.syn_node is not None:
            atomic_head_text = m.atomic_head.text
        parts = temp_text.split(atomic_head_text)
        last_part = ""
        if len(parts) > 1:
            last_part = parts[1]
        if mention is not None and mention.text == text:
            s += '<TR><TD><FONT COLOR="red">"%s(%s)%s"</FONT></TD></TR>' % (
            parts[0], escape_xml(atomic_head_text), last_part)
        # s += '<TR><TD><FONT COLOR="red">"%s" (%s)</FONT></TD></TR>' % (quote_dot1(text).replace("\l"," ").strip(),m.atomic_head.text)
        else:
            s += '<TR><TD>"%s(%s)%s"</TD></TR>' % (parts[0], escape_xml(atomic_head_text), last_part)
        # s += '<TR><TD>"%s" (%s)</TD></TR>' % (quote_dot1(text).replace("\l"," ").strip(), m.atomic_head.text)
    s += "</TABLE>>"
    # print "%s++\n" %s
    return '%s' % s


def sent_no_for_theory(theory):
    if theory is None:
        return None
    sent = theory.owner_with_type(Sentence)
    if sent: return sent.sent_no
    if isinstance(theory, Entity):
        return min(m.owner_with_type(Sentence).sent_no
                   for m in theory.mentions)
    if isinstance(theory, ActorMention):
        return theory.mention.owner_with_type(Sentence).sent_no
    if isinstance(theory, ICEWSEventMention):
        return min(p.actor.mention.owner_with_type(Sentence).sent_no
                   for p in theory.participants)
    return None


class DotNode(object):
    width = '1'
    margin = '0.05,0.05'
    style = 'filled'
    outline = '#000000'
    fontsize = 'default'

    @abc.abstractmethod
    def label(self):
        raise NotImplemented

    @abc.abstractmethod
    def fill_color(self):
        raise NotImplemented


    def tooltip(self):
        return ''

    def url(self):
        sent_no = sent_no_for_theory(self.value)
        if sent_no is None: return None
        doc = self.value.document
        return ('javascript:selectSentenceFromSentNo('
                '\\"sent-%s-%d\\", true);' % (doc.html_prefix, sent_no))

    def __init__(self, value):
        self.key = None
        self.value = value

    def to_dot(self, include_href=False, temp=False):
        # print "%s-----\n" % type(self)
        href = ''
        if include_href:
            href = self.url() or ''
            if href: href = ', href="%s"' % href
        return '  %s [label="%s",fillcolor="%s",tooltip="%s"%s];\n' % (
            dot_id(self.value), self.label(), self.fill_color(),
            escape_dot(self.tooltip()), href)

    def to_dot1(self, include_href=False, temp=False):
        href = ''
        if include_href:
            href = self.url() or ''
            if href: href = ', href="%s"' % href
        # return '  %s [label=%s];\n' % (dot_id(self.value),kk)
        return '  %s [label=%s,fillcolor="%s",tooltip="%s"%s];\n' % (
            dot_id(self.key), self.label(), self.fill_color(),
            escape_dot(self.tooltip()), href)

    @staticmethod
    def nodes_to_dot(nodes, include_href):
        s = ''
        grouped_nodes = defaultdict(dict)
        for node in nodes:
            grouped_nodes[type(node)][node.value] = node

        for (typ, group) in grouped_nodes.items():
            # print "%s\n" % typ
            if typ.fontsize == 'default':
                fontsize = ''
            else:
                fontsize = ',fontsize="%s"' % typ.fontsize
            s += ('{node [width="%s",height="0",margin="%s"'
                  'shape="record",style="%s",color="%s"%s];\n') % (
                     typ.width, typ.margin, typ.style, typ.outline, fontsize)
            for node in group.values():
                # print type(node)
                if type(node) is EntityDotNode1:  # check whether the node is Entity Node
                    # print "true\-------n"
                    s += node.to_dot1(include_href, False)
                    # print "%s\n" % s
                else:
                    s += node.to_dot(include_href, False)

            s += '}\n'
        return s


class SynDotNode(DotNode):
    outline = '#606060'

    def fill_color(self): return '#c0c0ff'

    def label(self):
        return '%s|%s' % (self.value.tag, quote_dot(self.value.text))

    def tooltip(self): return self.value.text


class EntityDotNode(DotNode):
    small = False
    width = property(lambda self: [DotNode.width, 0][self.small])
    margin = property(lambda self: [DotNode.margin, '0,0.01'][self.small])
    outline = '#606060'

    def fill_color(self):
        return '#c0ffc0'

    def label(self):
        if self.small:
            return escape_dot(name_for_entity(self.value), wrap=True)
        else:
            return entity_dot_label(self.value)

    def tooltip(self):
        return name_for_entity(self.value)

    def url(self):
        if not self.small: return DotNode.url(self)
        return 'javascript:showDocEntity(\\"entity-%s\\");' % dot_id(self.value)


class EntityDotNode1(DotNode):
    def __init__(self, key, value):
        super(DotNode,self).__init__()
        self.key = key
        self.value = value
        # print "%s\n"%value

    small = False
    width = property(lambda self: [DotNode.width, 0][self.small])
    margin = property(lambda self: [DotNode.margin, '0,0.01'][self.small])
    outline = '#606060'

    def fill_color(self):
        return '#c0ffc0'

    def label(self):
        if self.small:
            return escape_dot(name_for_entity(self.key), wrap=True)
        else:
            return entity_dot_label1(self.key, self.value)

    def tooltip(self):
        return name_for_entity(self.key)

    def url(self):
        if not self.small: return DotNode.url(self)
        return 'javascript:showDocEntity(\\"entity-%s\\");' % dot_id(self.key)


class FocusEntityDotNode(EntityDotNode):
    outline = '#000000'
    style = 'filled,bold'

    def fill_color(self): return '#a0ffa0'


class MentionDotNode(DotNode):
    small = False
    outline = '#606060'

    def fill_color(self):
        return '#c0ffc0'

    def label(self):
        if self.small:
            return escape_dot(self.value.text, wrap=True)
        else:
            return '%s|<%s>%s' % (entity_type(self.value),
                                  mention_port(self.value),
                                  quote_dot(self.value.text))

    def tooltip(self):
        return self.value.text


class ValMentionDotNode(DotNode):
    outline = '#606060'

    def fill_color(self): return '#c0c0c0'

    def label(self):
        return '%s|%s' % (self.value.value_type, quote_dot(self.value.text))

    def tooltip(self): return self.value.text


class PropDotNode(DotNode):
    style = 'rounded,filled'
    margin = '0.05,0.02'

    def fill_color(self):
        return {
            'verb': '#ffff00', 'set': '#c0c0ff',
            'copula': '#ffff00', 'comp': '#c0c0ff',
            'modifier': '#c0c000', 'noun': '#ffc0c0',
            'poss': '#c0c000', 'pronoun': '#ffc0c0',
            'loc': '#c0c000', 'name': '#ffc0c0',
        }.get(self.value.pred_type.value, '#ffff80')

    def label(self):
        prop = self.value
        label = prop.pred_type.value
        if hasattr(prop, 'status'):
            statuses = [prop.status]
        else:
            statuses = prop.statuses or ()
        for status in statuses:
            if status is not None and status != PropStatus.Default:  # @UndefinedVariable
                label += '|%s' % status.value
        if prop.head:
            label += '|%s' % quote_dot(prop.head.text, justify='c')
        return label

    def tooltip(self):
        if self.value.head:
            return self.value.head.text
        else:
            return self.value.pred_type.value


class RelDotNode(DotNode):
    style = 'rounded,filled'
    margin = '0.15,0.02'

    def fill_color(self):
        return '#ffff00'

    def label(self):
        rel = self.value
        if isinstance(rel, RelMention):
            reltype = rel.type
        else:
            reltype = rel.relation_type
        label = escape_dot('Relation %s' % reltype)
        if isinstance(rel, RelMention) and rel.raw_type:
            label += ' (%s)' % rel.raw_type
        if rel.tense and rel.tense != Tense.Unspecified:  # @UndefinedVariable
            label += '|tense: %s' % rel.tense.value
        if rel.modality:
            label += '|modality: %s' % rel.modality.value
        if isinstance(rel, RelMention) and rel.time_arg:
            label += '|'
            if rel.time_arg_role:
                label += 'time (%s): ' % rel.time_arg_role
            else:
                label += 'time: '
            label += quote_dot(rel.time_arg.text, justify='c')
        return label

    def tooltip(self):
        if isinstance(self.value, RelMention):
            return self.value.type
        else:
            return self.value.relation_type


class EventDotNode(DotNode):
    style = 'rounded,filled'
    margin = '0.15,0.02'

    # outline = '#000000:#000000'
    def fill_color(self):
        return '#ffff00'

    def label(self):
        event = self.value
        event_type_str_set = set()
        if isinstance(event,Event):
            event_type_str_set.add(tuple((event.event_type, 1.0)))
        elif isinstance(event,EventMention):
            event_type_str_set.add(tuple((event.event_type, event.score)))
            event_type_str_set.update(tuple((i.event_type, i.score)) for i in event.event_types)
            event_type_str_set.update(tuple((i.event_type, i.score)) for i in event.factor_types)
        label = escape_dot('Event %s' % ";".join("{}:{:.2f}".format(i[0],i[1]) for i in event_type_str_set))
        if event.tense and event.tense != Tense.Unspecified:  # @UndefinedVariable
            label += '|tense: %s' % event.tense.value
        if event.modality:
            label += '|modality: %s' % event.modality.value
        if event.genericity and event.genericity != Genericity.Specific:  # @UndefinedVariable
            label += '|genericity: %s' % event.genericity.value
        if event.polarity and event.polarity != Polarity.Negative:  # @UndefinedVariable
            label += '|polarity: %s' % event.polarity.value
        return label

    def tooltip(self):
        return self.value.event_type


class ICEWSEventMentionDotNode(DotNode):
    style = 'rounded,filled'
    margin = '0.15,0.02'

    def fill_color(self): return '#ffff00'

    def label(self):
        return 'Event %s|%s' % (escape_dot(self.value.event_code),
                                escape_dot(self.value.pattern_id))

    def tooltip(self):
        return self.value.event_code


class ICEWSActorMentionDotNode(DotNode):
    outline = '#606060'

    def fill_color(self):
        return '#c0ffc0'

    def label(self):
        if self.value.name:
            return '%s|%s' % (escape_dot(self.value.name),
                              quote_dot(self.value.text))
        else:
            return quote_dot(self.value.text)

    def tooltip(self):
        return self.value.name or self.value.text


def filter_propositions(propositions):
    """
    Given a set of Propositions, return the subset of Propositions
    that are 'interesting'.
    """
    filtered_propositions = set()
    if propositions is not None:
        for prop in propositions:
            if not is_boring_prop(prop):
                filtered_propositions.add(prop)
            for arg in prop.arguments:
                if arg.proposition:
                    filtered_propositions.add(arg.proposition)
    return filtered_propositions


def proposition_dot_nodes(doc, propositions):
    """
    Return a dot string that declares nodes for the given set of
    propositions, along with any entities or syn_nodes reachable from
    those propositions.
    """
    # Collect all nodes.
    prop_node_values = set()
    syn_node_values = set()
    mention_node_values = set()
    entity_node_values = set()
    for prop in propositions:
        prop_node_values.add(prop)
        for arg in prop.arguments:
            if arg.mention:
                entity = doc.mention_to_entity.get(arg.mention)
                if entity:
                    entity_node_values.add(entity)
                else:
                    mention_node_values.add(arg.mention)
            elif arg.syn_node:
                syn_node_values.add(arg.syn_node)
            else:
                prop_node_values.add(arg.value)
        # if prop.head: syn_node_values.add(prop.head)
        if prop.particle: syn_node_values.add(prop.particle)
        if prop.adverb: syn_node_values.add(prop.adverb)
        if prop.negation: syn_node_values.add(prop.negation)
        if prop.modal: syn_node_values.add(prop.modal)

    # Sort syn nodes by position.
    def syn_node_sort_key(syn_node):
        return (syn_node.start_char, -syn_node.end_char)

    syn_node_values = sorted(syn_node_values, key=syn_node_sort_key)

    return ([SynDotNode(v) for v in syn_node_values] +
            [MentionDotNode(v) for v in mention_node_values] +
            [EntityDotNode(v) for v in entity_node_values] +
            [PropDotNode(v) for v in prop_node_values])


def proposition_dot_edges(doc, propositions, focus=None,
                          use_mention_ports=True):
    edges = '{edge [labeldistance="0"];\n'
    for prop in propositions:
        args = [(arg.value, arg.role) for arg in prop.arguments]
        # pseudo-arguments:
        if prop.particle: args.append((prop.particle, '<particle>'))
        if prop.adverb: args.append((prop.adverb, '<adverb>'))
        if prop.negation: args.append((prop.negation, '<negation>'))
        if prop.modal: args.append((prop.modal, '<modal>'))
        # if prop.head:
        #    args.append( (prop.head, '<head>') ) # pseudo-arg for head.
        for arg_value, arg_role in args:
            src = dot_id(prop)
            entity = None
            if isinstance(arg_value, Mention):
                entity = doc.mention_to_entity.get(arg_value)
                dst = dot_id(entity or arg_value)
                if use_mention_ports:
                    dst += ':%s' % mention_port(arg_value)
            else:
                dst = dot_id(arg_value)
            style = PROP_EDGE_STYLE.get(arg_role, '')
            my_dir = prop_arg_dir(prop.pred_type, arg_role)
            if (focus is not None and focus == entity): my_dir = 'back'
            if my_dir != 'forward': (src, dst) = (dst, src)
            if arg_role.startswith('<') and arg_role.endswith('>'):
                arg_role = arg_role[1:-1]
                if style: style += ','
                style += 'fontname="Italic"'
            edges += '  %s->%s [dir="%s",label="%s",%s];\n' % (
                src, dst, my_dir, escape_dot(arg_role), style)
    return edges + '}\n'

def get_all_anchor_node_from_em(em:EventMention):
    ret = set()
    if em.anchor_node is not None:
        ret.add(em.anchor_node)
    for anchor in em.anchors:
        if anchor.anchor_node is not None:
            ret.add(anchor.anchor_node)
    return ret

def get_all_anchor_prop_from_em(em:EventMention):
    ret = set()
    if em.anchor_prop is not None:
        ret.add(em.anchor_prop)
    for anchor in em.anchors:
        if anchor.anchor_prop is not None:
            ret.add(anchor.anchor_prop)
    return ret

def event_dot_nodes(doc, events, include_prop_anchors=False):
    """
    Return a dot string that declares nodes for the given set of
    events, along with any entities or syn_nodes reachable from
    those events.
    """
    # Collect node values
    event_node_values = set()
    entity_node_values = set()
    entity_node_values1 = {}
    mention_node_values = set()
    valmention_node_values = set()
    syn_node_values = set()
    prop_node_values = set()
    if events:
        for event in events:
            event_node_values.add(event)
            if isinstance(event, EventMention):
                syn_node_values.update(get_all_anchor_node_from_em(event))
                if include_prop_anchors and event.anchor_prop is not None:
                    prop_node_values.update(get_all_anchor_prop_from_em(event))
            else:
                for em in event.event_mentions:
                    syn_node_values.update(get_all_anchor_node_from_em(em))
                    if include_prop_anchors and em.anchor_prop is not None:
                        prop_node_values.update(get_all_anchor_prop_from_em(em))
            for arg in event.arguments:
                if isinstance(arg, EventMentionArg):
                    # mention_node_values.add(arg.mention)
                    if arg.mention:
                        entity = doc.mention_to_entity.get(arg.mention)
                        if entity:
                            entity_node_values1[entity] = arg.mention
                            # entity_node_values.add(entity)
                        else:
                            mention_node_values.add(arg.mention)
                            # print "%s-----\n" % arg.mention
                    if arg.value_mention:
                        valmention_node_values.add(arg.value_mention)
                        # print "%s+++++\n" % arg.value_mention
                else:
                    if arg.entity:
                        entity_node_values.add(arg.entity)
                        # entity_node_values1[arg.entity]=arg.value.mentions[0]
                    if arg.value_entity:
                        valmention_node_values.add(arg.value.value_mention)
    # Display all nodes.
    return ([MentionDotNode(v) for v in mention_node_values] +
            [ValMentionDotNode(v) for v in valmention_node_values] +
            [SynDotNode(v) for v in syn_node_values] +
            [PropDotNode(v) for v in prop_node_values] +
            [EntityDotNode1(k, v) for k, v in entity_node_values1.items()] +
            [EntityDotNode(v) for v in entity_node_values] +
            [EventDotNode(v) for v in event_node_values])


def event_dot_edges(doc, events, include_prop_anchors=False, focus=None,
                    use_mention_ports=True):
    edges = '{edge [labeldistance="0",dir="none"];\n'
    if events:
        for event in events:
            for arg in event.arguments:
                label = escape_dot(arg.role)
                entity = None
                if isinstance(arg, EventMentionArg):
                    if arg.mention:
                        entity = doc.mention_to_entity.get(arg.mention)
                        dst = dot_id(entity or arg.mention)
                        if use_mention_ports:
                            dst += ':%s' % mention_port(arg.mention)
                    else:
                        dst = dot_id(arg.value_mention)
                else:
                    if arg.entity:
                        entity = arg.entity
                        dst = dot_id(arg.entity)
                    elif arg.event_mention:
                        dst = dot_id(arg.event_mention)
                    else:
                        dst = dot_id(arg.value.value_mention)
                if focus is not None and entity == focus:
                    edges += '  %s->%s [label="%s",dir="back"];\n' % (
                        dst, dot_id(event), label)
                else:
                    edges += '  %s->%s [label="%s"];\n' % (dot_id(event),
                                                           dst, label)

    edges += '}\n'
    edges += '{edge [labeldistance="0",dir="none",color="#00ff00"];\n'
    if events:
        for event in events:
            anchor_nodes = set()
            if isinstance(event, EventMention):
                anchor_nodes.update(get_all_anchor_node_from_em(event))

            else:
                for em in event.event_mentions:
                    anchor_nodes.update(get_all_anchor_node_from_em(em))
            for anchor in anchor_nodes:
                if anchor is None: continue
                edges += '  %s->%s [label="anchor"];\n' % (dot_id(anchor),
                                                           dot_id(event))
    edges += '}\n'
    if include_prop_anchors:
        edges += '{edge [labeldistance="0",dir="none",color="#00ff00"];\n'
        if events:
            for event in events:
                anchor_props = set()
                if isinstance(event, EventMention):
                    anchor_props.update(get_all_anchor_prop_from_em(event))
                else:
                    for em in event.event_mentions:
                        anchor_props.update(get_all_anchor_prop_from_em(em))
                for anchor in anchor_props:
                    if anchor is None: continue
                    edges += '  %s->%s [label="anchor-prop"];\n' % (
                        dot_id(anchor), dot_id(event))
        edges += '}\n'
    return edges


def empty_graph_msg(items, src):
    context = type(src).__name__
    return '<i>This %s contains no %s.</i>' % (context, items)


USE_SVG = True


def render_graphviz(graph, src, kind, binary='dot', zoomable=True):
    if isinstance(graph, str):
        graph = graph.encode('utf-8')

    if USE_SVG:
        my_format = '-Tsvg'
    else:
        my_format = '-Tpng'
    p = subprocess.Popen([binary, my_format], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    (dot_result, stderr) = p.communicate(graph)
    dot_result = dot_result.decode("utf-8")
    stderr = stderr.decode("utf-8")
    if p.returncode != 0:
        logger.critical(stderr)
        raise ValueError('Graphviz failed!')
    # Remove the xmldecl and doctype
    if USE_SVG:
        svg_graph = re.sub(r'^<\?xml[^>]+>\s*<!DOCTYPE[^>]+>', '', dot_result)
        svg_graph = svg_graph.replace('\r\n', '\n')
        # print "%s\n" % dot_result
        # print "%s" % svg_graph
        if zoomable:
            svg_graph = ZOOMABLE_GRAPH % svg_graph
        return svg_graph
    else:
        import base64
        img_data = base64.b64encode(dot_result)
        return '<img src=data:image/gif;base64,%s />' % img_data

class DependencySetSource(enum.Enum):
    PropositionSet = "PropositionSet"
    DependencySet = "DependencySet"

def get_dependency_set_from_sentence_theory(st:Sentence,dependency_set:DependencySetSource):
    if dependency_set is DependencySetSource.PropositionSet:
        return st.proposition_set or []
    elif dependency_set is DependencySetSource.DependencySet:
        return st.dependency_set or []
    else:
        raise NotImplemented

def dependencies_to_html(src, dependency_set:DependencySetSource):
    """src should be a sentence or a document."""
    if isinstance(src, Sentence):
        propositions = get_dependency_set_from_sentence_theory(src,dependency_set)
    else:
        propositions = sum([list(get_dependency_set_from_sentence_theory(s,dependency_set)) for s in src.sentences], [])
    propositions = filter_propositions(propositions)
    if not propositions:
        return empty_graph_msg('propositions', src)
    dot_nodes = proposition_dot_nodes(src.document, propositions)
    graph = 'digraph propositions {\n%s%s%s}\n' % (
        DOT_GRAPH_OPTIONS % dict(ranksep=0.1),
        DotNode.nodes_to_dot(dot_nodes, isinstance(src, Document)),
        proposition_dot_edges(src.document, propositions))
    return render_graphviz(graph, src, 'propositions')


def events_to_html(src):
    if isinstance(src, Sentence):
        events = src.event_mention_set
        # print "sentence\n"
    else:
        events = src.event_set
    if not events:
        return empty_graph_msg('events', src)
    dot_nodes = event_dot_nodes(src.document, events)
    graph = 'digraph events {\n%s%s%s}\n' % (
        DOT_GRAPH_OPTIONS % dict(ranksep=0.5),
        DotNode.nodes_to_dot(dot_nodes, isinstance(src, Document)),
        event_dot_edges(src.document, events))
    # print "%s--%s\n" % (isinstance(src, Sentence),graph)
    return render_graphviz(graph, src, 'events')


def relations_to_html(src):
    if isinstance(src, Sentence):
        relations = src.rel_mention_set
    else:
        relations = src.relation_set
    if not relations:
        return empty_graph_msg('relations', src)
    dot_nodes = relation_dot_nodes(src.document, relations)
    graph = 'digraph relations {\n%s%s%s}\n' % (
        DOT_GRAPH_OPTIONS % dict(ranksep=0.5),
        DotNode.nodes_to_dot(dot_nodes, isinstance(src, Document)),
        relation_dot_edges(src.document, relations))
    return render_graphviz(graph, src, 'relations')


def merged_graph_to_html(src,dependency_set_source:DependencySetSource):
    doc = src.document
    extra_nodes = []
    if isinstance(src, Sentence):
        propositions = get_dependency_set_from_sentence_theory(src,dependency_set_source)
        events = src.event_mention_set
        relations = src.rel_mention_set
        if INCLUDE_DISCONNECTED_ENTITIES_IN_MERGED_GRAPH and src.mention_set is not None:
            for mention in src.mention_set:
                entity = doc.mention_to_entity.get(mention)
                if entity: extra_nodes.append(EntityDotNode(entity))
    else:
        propositions = sum([list(get_dependency_set_from_sentence_theory(s,dependency_set_source)) for s in src.sentences], [])
        events = src.event_set
        relations = src.relation_set
        if INCLUDE_DISCONNECTED_ENTITIES_IN_MERGED_GRAPH:
            extra_nodes += [EntityDotNode(e) for e in doc.entity_set or ()]
    propositions = filter_propositions(propositions)
    if INCLUDE_DISCONNECTED_ENTITIES_IN_MERGED_GRAPH:
        if not (propositions or relations or events or extra_nodes):
            return empty_graph_msg('propositions, relations, events, or disconnected entities', src)
    else:
        if not (propositions or relations or events):
            return empty_graph_msg('propositions, relations, or events', src)
    dot_nodes = (relation_dot_nodes(doc, relations) +
                 proposition_dot_nodes(doc, propositions) +
                 event_dot_nodes(doc, events, include_prop_anchors=True) +
                 extra_nodes)
    graph = 'digraph merged {\n%s%s%s}\n' % (
        DOT_GRAPH_OPTIONS % dict(ranksep=0.1),
        DotNode.nodes_to_dot(dot_nodes, isinstance(src, Document)),
        (relation_dot_edges(doc, relations) +
         proposition_dot_edges(doc, propositions) +
         event_dot_edges(doc, events, include_prop_anchors=True)))
    return render_graphviz(graph, src, 'merged-graph')


def relation_dot_nodes(doc, relations):
    # Collect node values.
    rel_node_values = set()
    entity_node_values = set()
    mention_node_values = set()
    if relations:
        for relation in relations:
            rel_node_values.add(relation)
            if isinstance(relation, RelMention):
                for mention in (relation.left_mention, relation.right_mention):
                    entity = doc.mention_to_entity.get(mention)
                    if entity:
                        entity_node_values.add(entity)
                    else:
                        mention_node_values.add(mention)
            else:
                for entity in (relation.left_entity, relation.right_entity):
                    entity_node_values.add(entity)

    # Display all nodes.
    return ([MentionDotNode(v) for v in mention_node_values] +
            [EntityDotNode(v) for v in entity_node_values] +
            [RelDotNode(v) for v in rel_node_values])


def relation_dot_edges(doc, relations, focus=None, use_mention_ports=True):
    edges = '{edge [labeldistance="0"];\n'
    if relations:
        for rel in relations:
            swap_dir = False
            if isinstance(rel, RelMention):
                mentions = [rel.left_mention, rel.right_mention]
                swap_dir = (focus is not None and
                            focus == doc.mention_to_entity.get(rel.right_mention))
                sides = []
                for mention in mentions:
                    entity = doc.mention_to_entity.get(mention)
                    side = dot_id(entity or mention)
                    if use_mention_ports:
                        side += ':%s' % mention_port(mention)
                    sides.append(side)
            else:
                swap_dir = (focus is not None and focus == rel.right_entity)
                sides = [dot_id(e) for e in (rel.left_entity, rel.right_entity)]
            if swap_dir:
                edges += '  %s->%s->%s [dir="back"];\n' % (
                    sides[1], dot_id(rel), sides[0])
            else:
                edges += '  %s->%s->%s;\n' % (sides[0], dot_id(rel), sides[1])
    return edges + '}\n'


def prop_uses_entity(prop, entity):
    if prop.pred_type not in (PredType.verb, PredType.copula): return False  # @UndefinedVariable
    doc = entity.document
    return any(entity == doc.mention_to_entity.get(arg.mention)
               for arg in prop.arguments)


def event_uses_entity(event, entity):
    return any(entity == arg.entity for arg in event.arguments)


def relation_uses_entity(rel, entity):
    return entity in (rel.left_entity, rel.right_entity)


def entity_neighborhood_to_html(entity):
    doc = entity.document
    propositions = [prop for sent in doc.sentences
                    for prop in get_dependency_set_from_sentence_theory(sent,DependencySetSource.PropositionSet)
                    if prop_uses_entity(prop, entity)]
    propositions = filter_propositions(propositions)
    events = [event for event in (doc.event_set or ())
              if event_uses_entity(event, entity)]
    relations = [rel for rel in (doc.relation_set or ())
                 if relation_uses_entity(rel, entity)]
    focus = FocusEntityDotNode(entity)
    if not (propositions or relations or events):
        return ''
    dot_nodes = (relation_dot_nodes(doc, relations) +
                 proposition_dot_nodes(doc, propositions) +
                 event_dot_nodes(doc, events))
    dot_nodes = [focus] + [n for n in dot_nodes if n.value != entity]
    for node in dot_nodes: node.small = True
    if len(dot_nodes) == 1: return ''  # boring graph
    options = DOT_GRAPH_OPTIONS % dict(ranksep=0.5)
    extra_node = ('start [label="",width=0.1,height=0.1,'
                  'style="filled",fillcolor="#00ff00"];\n')
    extra_edge = 'start -> %s;\n' % dot_id(entity)
    graph = 'digraph merged {\n%s%s%s}\n' % (
        options,
        extra_node + DotNode.nodes_to_dot(dot_nodes, True),
        (extra_edge +
         relation_dot_edges(doc, relations, focus=entity,
                            use_mention_ports=False) +
         proposition_dot_edges(doc, propositions, focus=entity,
                               use_mention_ports=False) +
         event_dot_edges(doc, events, focus=entity,
                         use_mention_ports=False)))
    return render_graphviz(graph, entity, 'entity-neighborhood')


def entities_to_html(doc):
    edge_weights = defaultdict(lambda: 1)

    def connect_all_pairs(entities, weight):
        for e1 in entities:
            for e2 in entities:
                if id(e1) < id(e2):
                    edge_weights[e1, e2] += weight

    # Increase weight for entities that are mentioned in the same
    # sentence.
    for sent in doc.sentences:
        if sent.mention_set is None:
            continue
        entities = set(doc.mention_to_entity[m] for m in sent.mention_set
                       if m in doc.mention_to_entity)
        connect_all_pairs(entities, 0.1)

    # Increase weight for entities that are related by propositions
    for sent in doc.sentences:
        if sent.proposition_set is None:
            continue
        for prop in sent.proposition_set:
            mention_args = set(arg.mention for arg in prop.arguments
                               if arg.mention is not None)
            entity_args = set(doc.mention_to_entity[m] for m in mention_args
                              if m in doc.mention_to_entity)
            connect_all_pairs(entity_args, 1)

    # Prune out "boring" entities
    interesting_entities = set()
    # Any weight over 1.1 makes it interesting.
    for (e1, e2), weight in edge_weights.items():
        if weight > 1.1:
            interesting_entities.add(e1)
            interesting_entities.add(e2)
    # Any entity that appears in >1 sentence is interesting.
    for entity in doc.entity_set or ():
        if len(set(m.owner_with_type(Sentence)
                   for m in entity.mentions)) > 1:
            interesting_entities.add(entity)

    # Draw nodes.
    dot_nodes = [EntityDotNode(e) for e in interesting_entities]
    for node in dot_nodes: node.small = True

    # increase edge weight based on mention frequency.
    for (e1, e2), weight in edge_weights.items():
        weight *= min(len(e1.mentions), 5) / 2.0
        weight *= min(len(e2.mentions), 5) / 2.0
        edge_weights[e1, e2] = weight

    # Draw edges
    edges = '{\n'
    if edge_weights:
        MAX_WEIGHT = max(edge_weights.values())
        for (e1, e2), weight in edge_weights.items():
            if e1 not in interesting_entities: continue
            if e2 not in interesting_entities: continue

            assert id(e1) < id(e2)
            w = 1.0 * min(weight, MAX_WEIGHT) / MAX_WEIGHT
            color = '#%02x%02x%02x' % (220, (240 - 240 * int(w)), (240 - 240 * int(w)))
            attribs = 'weight=%s' % weight
            attribs += ',len=%s' % (1.5 - 1.3 * min(w, MAX_WEIGHT))
            attribs += ',color="%s"' % color
            if weight < 2:
                attribs += ',style="dashed"'
            elif weight > MAX_WEIGHT / 3 and weight > 3:
                attribs += ',style="bold"'
            # print attribs
            edges += '  %s -- %s [%s];\n' % (dot_id(e1), dot_id(e2), attribs)
    edges += '}\n'

    options = 'node [fontsize="8"];\n'
    # options += 'ratio=0.5;\n'

    graph = 'graph entities {\n%s%s%s}\n' % (
        options, DotNode.nodes_to_dot(dot_nodes, True), edges)

    # neato, twopi, circo, fdp, sfdp
    return DOC_ENTITY_GRAPH % (
        render_graphviz(graph, doc, 'entities', 'fdp'))


def icews_events_to_html(doc):
    icews_events = doc.icews_event_mention_set
    if not icews_events:
        return empty_graph_msg('icews_events', doc)
    dot_nodes = icews_event_dot_nodes(doc, icews_events)
    graph = 'digraph icews_events {\n%s%s%s}\n' % (
        DOT_GRAPH_OPTIONS % dict(ranksep=0.5) + "\nordering=\"out\";",
        DotNode.nodes_to_dot(dot_nodes, True),
        icews_event_dot_edges(doc, icews_events))
    return render_graphviz(graph, doc, 'icews_events')


def icews_event_dot_nodes(doc, icews_events):
    # Collect node values.
    event_values = set()
    actor_values = set()
    for event in icews_events:
        event_values.add(event)
        for participant in event.participants:
            actor_values.add(participant.actor)
    return ([ICEWSEventMentionDotNode(v) for v in event_values] +
            [ICEWSActorMentionDotNode(v) for v in actor_values])


def icews_event_dot_edges(doc, icews_events):
    edges = '{\n'
    for event in icews_events:
        for participant in sorted(event.participants, key=lambda x: x.role):
            if participant.role == 'SOURCE':
                edges += '  %s -> %s;' % (
                    dot_id(participant.actor), dot_id(event))
            elif participant.role == 'TARGET':
                edges += '  %s -> %s;' % (
                    dot_id(event), dot_id(participant.actor))
            else:
                edges += ('  %s -> %s [label="%s",color="#800000",'
                          'dir="none"];' % (
                              dot_id(event), dot_id(participant.actor),
                              escape_dot(participant.role)))
    return edges + '}\n'


###########################################################################
## Sentence Details
###########################################################################

def write_sentence_details_page(sentence, out_dir, show_merged_graphs=False):
    panes = [
        ('Parse', parse_to_html(sentence)),
        ('Propositions', dependencies_to_html(sentence, DependencySetSource.PropositionSet)),
        ('UniversalDependencies', dependencies_to_html(sentence, DependencySetSource.DependencySet)),
        ('Relations', relations_to_html(sentence)),
        ('Events', events_to_html(sentence))
    ]
    if show_merged_graphs:
        panes.append(('Merged Graph PropositionSet', merged_graph_to_html(sentence,DependencySetSource.PropositionSet)))
        panes.append(('Merged Graph DependencySet', merged_graph_to_html(sentence,DependencySetSource.DependencySet)))

    tabs_html = '<ul class="nav-tabs">\n'
    panes_html = '<div class="nav-panes">\n'
    for (tab, pane) in panes:
        tab_id = tab.split()[0].lower()
        tabs_html += '<li id="%s">%s</li>' % (tab_id, tab)
        panes_html += SENTENCE_DETAILS_PANE % dict(tab_id=tab_id, body=pane)
    tabs_html += '</ul>\n'
    panes_html += '</div>\n'

    # Save the details page.
    details_page = HTML_PAGE % dict(
        title='Sentence Details', css='sentence-details',
        script='$(document).ready(function() {setupDetailsFrame(); });',
        body=tabs_html + panes_html)
    details_filename = '%s-sent-%d-details.html' % (
        sentence.document.html_prefix, sentence.sent_no)
    save(details_page, out_dir, details_filename)

    # Save the details context page.
    context_page = HTML_PAGE % dict(
        title='Sentence Context', css='sent-context',
        script='$(document).ready(function() {setupSentContextFrame(); });',
        body=SENT_CONTEXT_BODY % dict(
            sent_no=sentence.sent_no,
            docid=sentence.document.docid))
    context_filename = '%s-sent-%d-nav.html' % (
        sentence.document.html_prefix, sentence.sent_no)
    save(context_page, out_dir, context_filename)


###########################################################################
## Document Entities
###########################################################################

DOC_ENTITIES_BODY = '''
<table class="entities">
%s
</table>
'''

ENTITY_HTML = '''
<div class="entity collapsed-entity %(css)s" id="%(anchor)s">
<div class="mention-info">%(mention_info)s</div>
<h2><a class="expand-entity" href="#"
name="%(anchor)s">%(name)s</a></h2>
<div class="entity-mentions">
<table class="entity-mentions">
%(mention_rows)s
</table>
<div class="entity-neighborhood">
%(neighborhood_graph)s
</div>
</div>
</div>
'''

ENTITY_MENTION_ROW = '''
<tr class="mention">
<td class="location"><a
href="%(html_prefix)s-sent-%(sent_no)d-details.html"
>Sentence %(sent_no)s</a></td>
<td align="center" class="mention_type">%(type)s</td>
<td class="left"><font color="#848482"><i>%(left)s</i></font></td>
<td class="mention"><b><font size="4pt">%(before_head)s</font> <font color="red" size="4pt">%(atomicHead)s</font><font size="4pt"> %(after_head)s</font></b></td>
<td class="right"><font color="#848482"><i>%(right)s</i></font></td>
'''


# <td align="center" class="atomicHead">%(atomicHead)s</td>
def name_for_entity(entity):
    names = defaultdict(int)
    for mention in entity.mentions:
        score = min(20, len(mention.text))
        if len(mention.text) > 20: score -= 0.001 * len(mention.text)
        if mention.mention_type == MentionType.name: score += 40
        names[mention.text] += score
    best_name, _best_score = sorted(names.items(), key=lambda t: t[1])[-1]
    # print 'Best name: %r (%s)' % (best_name, best_score)
    return best_name


def write_doc_entities_page(doc, out_dir):
    context_filename = '%s-entities-nav.html' % (doc.html_prefix)

    # Begin by graphing the entities.
    entities_html = entities_to_html(doc)

    # Next, add a table.
    CONTEXT_SIZE = 30

    def sortkey(entity):
        return -len(entity.mentions)

    entities = sorted(doc.entity_set or (), key=sortkey)
    for i, entity in enumerate(entities):
        mention_rows = ''
        sentences = set()
        for mention in entity.mentions:
            sent = mention.owner_with_type(Sentence)
            sentences.add(sent)
            s, e = mention.start_char, mention.end_char

            left_context = doc.get_original_text_substring(
                max(sent.start_char, s - CONTEXT_SIZE), s - 1)
            if sent.start_char < s - CONTEXT_SIZE:
                left_context = '...%s' % left_context
            right_context = doc.get_original_text_substring(
                e + 1, min(e + CONTEXT_SIZE, sent.end_char))
            if sent.end_char > e + CONTEXT_SIZE:
                right_context += '...'

            temp_mention = escape_xml(mention.text)
            atomic_head_text = mention.text
            if mention.atomic_head is not None:     
                atomic_head_text = mention.atomic_head.text
                
            # Fix for name mentions that aren't in an NPP 
            if (mention.syn_node is not None and 
                mention.syn_node.parent == mention.atomic_head):
                atomic_head_text = mention.text

            temp_head = escape_xml(atomic_head_text)
            parts = temp_mention.split(temp_head)
            # print "%s--%s"% (parts[0],parts[1])
            mention_rows += ENTITY_MENTION_ROW % dict(
                html_prefix=doc.html_prefix,
                sent_no=sent.sent_no,
                left=escape_xml(left_context),
                mention=escape_xml(mention.text),
                before_head=parts[0],
                after_head=parts[1],
                type=escape_xml(mention.mention_type.value),
                atomicHead=escape_xml(atomic_head_text),
                right=escape_xml(right_context))
        css = ''
        if (i % 2 == 0): css += ' even-entity'
        if (i == len(entities) - 1): css += ' last-entity'
        etype = entity.entity_type
        if entity.entity_subtype != 'UNDET':
            etype = '%s %s' % (entity.entity_subtype, etype)
        mention_info = '<b>%s</b>, mentioned in %d sentence%s' % (
            etype, len(sentences), ('s', '')[len(sentences) == 1])
        neighborhood_graph = entity_neighborhood_to_html(entity)
        entities_html += ENTITY_HTML % dict(
            anchor='entity-%s' % dot_id(entity),
            name=escape_xml(name_for_entity(entity)),
            etype=escape_xml(entity_type(entity)),
            mention_info=mention_info,
            num_mentions=len(entity.mentions),
            mention_rows=mention_rows,
            neighborhood_graph=neighborhood_graph,
            css=css)
    script = ('$(document).ready(function() '
              '{setupDocEntitiesFrame("%s"); });' % context_filename)
    page = HTML_PAGE % dict(
        title='Entities', css='doc-entities',
        script=script,
        body=entities_html)
    save(page, out_dir, '%s-entities.html' % doc.html_prefix)

    # The graph's context page.
    context = HTML_PAGE % dict(
        title='Context', css='doc-context', script='',
        body='Entities for <span class="docid">%s</span>' % doc.docid)
    save(context, out_dir, context_filename)


###########################################################################
## Document Text
###########################################################################

TEXT_PAGE_BODY = '''
<div class="text-options">
<input id="toggle-prons" type="checkbox" checked> Mark Pronouns
<input id="toggle-names" type="checkbox" checked> Mark Names
<input id="toggle-descs" type="checkbox" checked> Mark Descriptions
%(other_mark)s
<input id="toggle-unprocessed" type="checkbox" checked> Show Unprocessed
</div>
<div class="doc-body mark-prons mark-names mark-desc mark-icews-actors"
     id="doc-body">
%(body)s
</div>
'''

MARK_ICEWS = '''
<input id="toggle-icews-actors" type="checkbox" checked> Mark ICEWS Actors
'''


def write_doc_text_page(doc, out_dir):
    html = ''
    pos = doc.original_text.start_char
    for sent in doc.sentences:
        if sent.start_char > pos:
            text = doc.get_original_text_substring(pos, sent.start_char - 1)
            a, b, c = re.match(r'^(\s*)([\s\S]*\S)?(\s*)$', text, re.UNICODE).groups()
            if b:
                b = escape_xml(b)
                b = b.replace('\n', '</span>\n<span class="unprocessed">', 1)
            else:
                b = ''
            html += '<span class="unprocessed">%s</span>' % (
                (a + b + c).replace('\n', '<br/>\n'))
        elif sent.sent_no > 0:
            html += ' '
        html += sentence_to_html(sent)
        pos = sent.end_char + 1
    if pos < doc.original_text.end_char:
        text = doc.get_original_text_substring(pos, doc.original_text.end_char)
        html += '<span class="unprocessed">%s</span>' % (
            escape_xml(text).replace('\n', '<br/>\n'))
    html += '</div>'

    if doc.icews_actor_mention_set:
        other_mark = MARK_ICEWS
    else:
        other_mark = ''
    page = HTML_PAGE % dict(
        title=escape_xml(doc.docid), css='doc-text',
        script=DOCUMENT_TEXT_SCRIPT % dict(doc_url_prefix=doc.html_prefix),
        body=TEXT_PAGE_BODY % dict(body=html, other_mark=other_mark))
    save(page, out_dir, doc.html_prefix + '.html')


def sentence_to_html(sent, highlights=None):
    """
    @param highlights: A dictionary mapping token->CSS class
    """
    # Get the text of each token.
    if highlights is None:
        highlights = dict()
    tok_list = list(sent.token_sequence)
    if USE_ORIGINAL_TEXT_FOR_TOKENS:
        tok_html = [escape_xml(sent.get_original_text_substring(
            tok.start_char, tok.end_char))
            for tok in tok_list]
    else:
        tok_html = [escape_xml(tok.text)
                    for tok in tok_list]

    # Add any token highlights.
    for i, tok in enumerate(tok_list):
        if tok in highlights:
            tok_html[i] = '<span class="%s">%s</span>' % (
                highlights[tok], tok_html[i])

    mention_to_icews_actor = dict((a.mention, a) for a in
                                  (sent.document.icews_actor_mention_set
                                   or ()))

    def mention_sort_key(m):
        if m.syn_node is not None:
            return m.syn_node.end_char - m.syn_node.start_char
        return m.end_token.end_char - m.start_token.start_char

    mentions = []
    if sent.mention_set is not None:
        mentions = sorted(sent.mention_set, key=mention_sort_key)

    # Mark the mentions
    for mention in mentions:
        if mention.mention_type not in (MentionType.name, MentionType.pron,  # @UndefinedVariable
                                        MentionType.desc):  # @UndefinedVariable
            continue

        s = None
        e = None
        if mention.syn_node is not None:
            s = tok_list.index(mention.syn_node.start_token)
            e = tok_list.index(mention.syn_node.end_token)
        else:
            s = tok_list.index(mention.start_token)
            e = tok_list.index(mention.end_token)

        entity_type = mention.entity_type
        if mention.entity_subtype != 'UNDET':
            entity_type += '.' + mention.entity_subtype

        entity = sent.document.mention_to_entity.get(mention)
        if entity is None:
            entity_css = ''
        else:
            entity_css = ' entity-%s' % dot_id(entity)

        tok_html[s] = '<span class="mention %s%s">%s' % (
            mention.mention_type.value, entity_css, tok_html[s])
        # print tok_html[s]
        tok_html[e] = '%s</span>' % tok_html[e]
        # Mark ICEWS actor-mentions as well.
        actor = mention_to_icews_actor.get(mention)
        if actor:
            label = actor.name or 'UNKNOWN-ACTOR'
            spanclass = 'icews-actor'
            if icews_same_actor_as_parent(actor, mention_to_icews_actor):
                label = ''
            if actor.actor_uid:
                label_title = 'Actor %s' % actor.actor_uid
                if label == 'UNKNOWN-ACTOR': label = label_title
            elif actor.paired_agent_uid:
                label_title = 'Agent %s for actor %s' % (
                    actor.paired_agent_uid, actor.paired_actor_uid)
                if label == 'UNKNOWN-ACTOR': label = label_title
                if actor.actor_agent_pattern:
                    label_title += ' (%s)' % actor.actor_agent_pattern
            else:
                label_title = 'UNKNOWN-ACTOR'
            tok_html[s] = ('<span class="%s"><span class="text">%s'
                           % (spanclass, tok_html[s]))
            tok_html[e] = ('%s</span><span class="label" title="%s">%s</span>'
                           '</span>' % (tok_html[e], label_title, label))

    # Put the tokens back together, including whitespace.
    sid = u'sent-%s-%d' % (sent.document.html_prefix, sent.sent_no)
    sentence_text = u'<span class="sentence" id="%s" name="%s">' % (sid, sid)
    pos = sent.start_char
    for tok, s in zip(tok_list, tok_html):
        # Add the text between the tokens.
        unprocessed = sent.get_original_text_substring(pos, tok.start_char - 1)
        a, b, c = re.match(r'^(\s*)([\s\S]*\S)?(\s*)$', unprocessed, re.UNICODE).groups()
        if b:
            b = escape_xml(b)
            b = b.replace('\n', '</span>\n<span class="unprocessed">', 1)
            sentence_text += ('%s<span class="unprocessed">%s</span>%s' %
                              (a, b, c))
        else:
            sentence_text += a + c
        # Add the token text.
        sentence_text += s
        pos = tok.end_char + 1
    sentence_text += '</span>'

    # [XXXX]
    # Todo: reduce <span class="x">...</span>\s+</span class="x">...</span>

    return sentence_text.replace('\n', '<br/>')


def icews_same_actor_as_parent(actor, mention_to_icews_actor):
    node = actor.mention.syn_node.parent
    ok_node_types = (MentionType.name, MentionType.pron, MentionType.desc)  # @UndefinedVariable
    while node is not None:
        if ((node.mention is not None) and
                (node.mention.mention_type in ok_node_types)):
            p = mention_to_icews_actor.get(node.mention)
            if p:
                return (actor.actor_uid == p.actor_uid and
                        actor.paired_actor_uid == p.paired_actor_uid and
                        actor.paired_agent_uid == p.paired_agent_uid)
        node = node.parent
    return False


def write_doc_context_page(doc, out_dir):
    context_filename = '%s-nav.html' % (doc.html_prefix)
    context = HTML_PAGE % dict(
        title='Context', css='doc-context', script='',
        body='Document <span class="docid">%s</span>' % doc.docid)
    save(context, out_dir, context_filename)


###########################################################################
## Navigation/Context Frames
###########################################################################

def doc_nav_to_html(doc, show_doc_entities, show_doc_graphs, show_merged_graphs):
    # The document itself
    s = ('<li class="jstree-open doc"><a class="doc no-details" href="%s.html" '
         'target="serifxmlTextFrame" title="%s" id="doc-%s">%s</a>\n' %
         (doc.html_prefix, doc.filename, doc.html_prefix, doc.docid))
    s += ' <ul>\n'
    # Sentences
    s += ('  <li class="jstree-closed"><a class="sent-details" '
          'href="%s.html#sent-%s-0" target="serifxmlTextFrame"> '
          'Sentences <span class="count">(%d)</span></a><ul>\n' %
          (doc.html_prefix, doc.html_prefix, len(doc.sentences)))
    for sentno, sent in enumerate(doc.sentences):
        sent_label = '<span class="sentno">%d:</span> %s' % (
            sentno, escape_xml(sent.text))
        s += ('    <li><a href="%s.html#sent-%s-%d" '
              'class="sent-details" target="serifxmlTextFrame">%s</a></li>\n'
              % (doc.html_prefix, doc.html_prefix, sentno, sent_label))
    s += '  </ul></li>\n'
    # Entities
    if show_doc_entities:
        s += ('  <li><a href="%s-entities.html" target="serifxmlDetailsFrame" '
              'class="doc-details">Entities <span class="count">(%d)</span>'
              '</a></li>' % (doc.html_prefix, len(doc.entity_set or ())))
    # Graphs
    if show_doc_graphs:
        graph_count = {
            'propositions': sum(len(s.proposition_set or ()) for s in doc.sentences),
            'relations': len(doc.relation_set or ()),
            'events': len(doc.event_set or ()),
            'merged graph': (sum(len(s.proposition_set or ()) for s in doc.sentences) +
                             len(doc.relation_set or ()) + len(doc.event_set or ())),
            'icews events': len(doc.icews_event_mention_set or ())}
        graphs = ['propositions', 'relations', 'events', 'icews events']
        if show_merged_graphs:
            graphs.append('merged graph')
        for graph in graphs:
            if graph_count[graph] == 0: continue  # leave out empty graphs.
            url = '%s-%s.html' % (doc.html_prefix, graph.replace(' ', '-'))
            s += ('    <li><a href="%s" target="serifxmlDetailsFrame" class='
                  '"doc-details">%s <span class="count">(%d)</span></a></li>\n' % (
                      url, graph.capitalize(), graph_count[graph]))

    s += ' </ul>\n'
    s += '</li>\n'
    return s


def write_nav_page(doc_nav, out_dir):
    nav_page = HTML_PAGE % dict(
        title='SerifXML Viewer Navigation', css='navigation',
        script='$(document).ready(function() {setupDocNavFrame(); });',
        body=DOC_NAV_BODY % doc_nav)
    save(nav_page, out_dir, 'nav.html')


###########################################################################
## Document-level graphs
###########################################################################

def write_doc_graph_page(doc, kind, out_dir, graph):
    graph_filename = '%s-%s.html' % (doc.html_prefix, kind)
    context_filename = '%s-%s-nav.html' % (doc.html_prefix, kind)
    kind_txt = ' '.join(w.capitalize() for w in kind.split('-'))

    # The graph page.
    script = ('$(document).ready(function() '
              '{setupDocGraphFrame("%s"); });' % context_filename)
    graph_page = HTML_PAGE % dict(
        title='%s %s' % (doc.docid, kind_txt), css='doc-graph',
        script=script, body=graph)
    save(graph_page, out_dir, graph_filename)

    # The graph's context page.
    graph_context = HTML_PAGE % dict(
        title='Context', css='doc-context', script='',
        body=kind_txt + ' for <span class="docid">%s</span>' % doc.docid)
    save(graph_context, out_dir, context_filename)


###########################################################################
## Helper Functions
###########################################################################

def save(s, out_dir, filename):
    path = os.path.join(out_dir, filename)
    logger.debug("Saving: {}".format(path))
    if isinstance(s, str): s = s.encode('utf-8')
    out = open(path, 'wb')
    out.write(s)
    out.close()


def is_newer(f1, f2):
    if not os.path.exists(f1): return False
    return (os.stat(f1)[stat.ST_MTIME] > os.stat(f2)[stat.ST_MTIME])


###########################################################################
## Command-line Interface
###########################################################################

###########################################################################
## Document View Pages
###########################################################################

def write_document_pages(doc, out_dir, options):
    if options.nav_only:
        logger.info(' [nav-only]')
        return
    context_file = os.path.join(out_dir, doc.html_prefix + '-nav.html')
    if (not options.force) and is_newer(context_file, doc.filename):
        logger.warning('Skipping doc {} due to {} is newer than {}.'.format(doc.docid,context_file,doc.filename))
        return
    # Document text page.
    write_doc_text_page(doc, out_dir)
    # Sentence pages
    if not SKIP_SENTENCE_PAGES:
        for _n, sentence in enumerate(doc.sentences):
            write_sentence_details_page(sentence, out_dir, options.show_merged_graphs)
    # document-level graphs.
    if options.show_doc_graphs:
        write_doc_graph_page(doc, 'propositions', out_dir,
                             dependencies_to_html(doc,DependencySetSource.PropositionSet))
        write_doc_graph_page(doc, 'dependencies', out_dir,
                             dependencies_to_html(doc,DependencySetSource.DependencySet))
        write_doc_graph_page(doc, 'relations', out_dir,
                             relations_to_html(doc))
        write_doc_graph_page(doc, 'events', out_dir,
                             events_to_html(doc))
        write_doc_graph_page(doc, 'icews-events', out_dir,
                             icews_events_to_html(doc))
        if options.show_merged_graphs:
            write_doc_graph_page(doc, 'merged-graph-propositions', out_dir,merged_graph_to_html(doc,DependencySetSource.PropositionSet))
            write_doc_graph_page(doc, 'merged-graph-dependencies', out_dir,merged_graph_to_html(doc,DependencySetSource.DependencySet))

    if options.show_doc_entities:
        write_doc_entities_page(doc, out_dir)
    # Document context page
    write_doc_context_page(doc, out_dir)
    logger.info('[done]')


###########################################################################
## Searches
###########################################################################

SEARCH_PAGE_BODY = '''
<div class="text-options">
<input id="toggle-prons" type="checkbox"> Mark Pronouns
<input id="toggle-names" type="checkbox"> Mark Names
<input id="toggle-descs" type="checkbox"> Mark Descriptions
<input id="toggle-icews-actors" type="checkbox"> Mark ICEWS Actors
</div>
<div class="doc-body" id="doc-body">
%(body)s
</div>
'''

SEARCHER_MATCH_SENTENCE_HTML = '''
<div class="match %(even_or_odd)s-match">
  <div class="match-location">%(sent_location)s</div>
  <div class="context">%(left_context)s</div>
%(text)s
  <div class="context">%(right_context)s</div>
  <div class="clear"></div>
</div>
'''


class DocSearcher(object):
    PREFIX = 'Search'
    CONTEXT_SIZE = 1000

    def __init__(self, name, out_dir):
        self.name = name
        self.out_dir = out_dir
        self.html_name = name + '.html'  # add escaping etc??
        self.nav_html_name = name + '-nav.html'
        self.items = []

    def _add_sentence_match(self, sentence, highlighted_tokens=None,
                            highlighted_synnodes=None):
        if highlighted_tokens is None:
            highlighted_tokens = dict()
        if highlighted_synnodes is None:
            highlighted_synnodes = dict()
        doc = sentence.document
        loc = '%s<br>sentence %s' % (escape_xml(doc.docid), sentence.sent_no)
        s, e = sentence.start_char, sentence.end_char
        if s - self.CONTEXT_SIZE <= 0:
            left_context = doc.get_original_text_substring(0, max(0, s - 1))
        else:
            left_context = '...' + doc.get_original_text_substring(
                s - self.CONTEXT_SIZE, max(0, s - 1))
        if e + self.CONTEXT_SIZE > doc.original_text.end_char:
            right_context = doc.get_original_text_substring(
                e + 1, e + self.CONTEXT_SIZE)
        else:
            right_context = doc.get_original_text_substring(
                e + 1, e + self.CONTEXT_SIZE) + '...'
        even_or_odd = (len(self.items) % 2 == 0) and 'even' or 'odd'
        self.items.append(SEARCHER_MATCH_SENTENCE_HTML % dict(
            text=sentence_to_html(sentence, highlighted_tokens),
            left_context=left_context,
            right_context=right_context,
            sent_location=loc,
            even_or_odd=even_or_odd))
        # Write any sentence detail pages associated with this
        # sentence.  Note: we may write the same sentence's page more
        # than once.
        write_sentence_details_page(sentence, self.out_dir)

    def update(self, doc):
        raise AssertionError('Abstract base class')

    def write_pages(self):
        # Write the search's page.
        script = ('$(document).ready(function() '
                  '{setupSearchFrame(); });')
        search_page = HTML_PAGE % dict(
            title=escape_xml(self.name), css='doc-search', script=script,
            body=SEARCH_PAGE_BODY % dict(body=''.join(self.items)))
        save(search_page, self.out_dir, self.html_name)

        # The search's context page.
        search_context = HTML_PAGE % dict(
            title='Context', css='doc-context', script='',
            body='%s: "%s"' % (self.PREFIX, escape_xml(self.name)))
        save(search_context, self.out_dir, self.nav_html_name)

    def nav_to_html(self):
        return ('<li class="jstree-open doc"><a class="doc no-details" '
                'href="%s" target="serifxmlTextFrame" title="%s" '
                'id="terms-%s">%s: %s</a>\n' %
                (self.html_name, self.name, self.name,
                 self.PREFIX, self.name))


TERM_SEARCH_BOX = '''
<div class="searcher-info">
<h3>%(name)s: Search Terms</h3>
<div class="info-body">
%(terms)s
</div>
</div>
'''


class TermSearcher(DocSearcher):
    PREFIX = 'Term Search'

    def __init__(self, filename, out_dir):
        DocSearcher.__init__(self, os.path.split(filename)[1], out_dir)
        terms_str = open(filename, 'rb').read()
        # Strip comments
        terms_str = re.sub('#.*', '', terms_str)
        filter_terms = terms_str.split()
        simple_terms = [w for w in filter_terms if '+' not in w]
        multiword_terms = [w for w in filter_terms if '+' in w]

        # For single-word terms, use a single regexp.
        stems = [re.escape(self.stem(w)) for w in simple_terms]
        if stems:
            self.filter_re = re.compile('^(%s).*$' % '|'.join(stems),
                                        re.IGNORECASE)
        else:
            self.filter_re = None

        # Multiword terms
        self.multiword_terms = {}
        for t in multiword_terms:
            dst = self.multiword_terms
            for piece in t.split('+'):
                dst = dst.setdefault(self.stem(piece), {})
            dst[1] = True

        # Add an item that lists the terms we searched for.
        self.items.append(TERM_SEARCH_BOX % dict(
            name=escape_xml(self.name),
            terms=escape_xml(terms_str)))

    def update(self, doc):
        num_hits = 0
        for sentence in doc.sentences:
            tok_matches = self.match(sentence)
            if tok_matches:
                hl_toks = dict((tok, 'highlight') for tok in tok_matches)
                self._add_sentence_match(sentence, highlighted_tokens=hl_toks)
                num_hits += 1
        return num_hits

    @staticmethod
    def stem(word):
        return re.sub(r'(...)[ey]$', r'\1', word).lower()

    def match(self, sentence):
        tok_matches = set()
        if self.filter_re:
            for tok in sentence.token_sequence:
                if self.filter_re.match(tok.text):
                    # print '  Token: %r' % tok.text
                    tok_matches.add(tok)
        for toks in self.multiword_match(sentence.token_sequence):
            # print '  Multiword: %r' % ' ... '.join(t.text for t in toks)
            tok_matches.update(toks)
        return tok_matches

    def multiword_match(self, tokens, term_dict=None, start_tok=0):
        if term_dict is None: term_dict = self.multiword_terms
        for toknum in range(start_tok, len(tokens)):
            for first, rest in term_dict.items():
                if first == 1: continue
                if tokens[toknum].text.lower().startswith(first):
                    # base case
                    if 1 in rest: yield [tokens[toknum]]
                    # recursive case
                    for result in self.multiword_match(tokens, rest, toknum + 1):
                        result.append(tokens[toknum])
                        if start_tok == 0: result = result[::-1]
                        yield result


class PropSearcher(DocSearcher):
    PREFIX = 'Proposition Search'

    def __init__(self, filename, out_dir):
        DocSearcher.__init__(self, os.path.split(filename)[1], out_dir)
        search_str = open(filename, 'rb').read()
        self.matchers = []
        self.parse_search_terms(search_str)

    def update(self, doc):
        num_hits = 0
        for sentence in doc.sentences:
            hl_toks = {}
            for prop in sentence.proposition_set:
                for matcher in self.matchers:
                    if matcher.match(prop):
                        self.highlight_toks(prop, hl_toks)
            if hl_toks:
                self._add_sentence_match(sentence, hl_toks)
                num_hits += 1
        return num_hits

    def highlight_toks(self, prop, hl_toks, css='highlight'):
        for arg in prop.arguments:
            if arg.syn_node:
                for tok in arg.syn_node.tokens:
                    hl_toks[tok] = 'highlight-arg'
            if arg.mention:
                for tok in arg.mention.syn_node.tokens:
                    hl_toks[tok] = 'highlight-arg'
            if arg.proposition:
                self.highlight_toks(arg.proposition, hl_toks, 'highlight-arg')
        for tok in prop.head.tokens:
            hl_toks[tok] = css

    TOKEN_RE = re.compile(r'(?P<start_prop>(?P<prop_name>\w+)\()|'
                          r'(?P<end_prop>\))|'
                          r'(?P<arg>(?P<arg_name>\w+)=)|'
                          r'(?P<str>\"[^\"]*\")|'
                          r'(?P<comma>,)'
                          r'(?P<space>\s+)'
                          r'(?P<error>.)'
                          r'(?P<comment>#.*)')

    def parse_search_terms(self, s):
        next_arg = {}
        matchers = []
        for m in self.TOKEN_RE.finditer(s):
            if m.group('start_prop'):
                matchers.append(self.PropMatcher(m.group('prop_name')))
            elif m.group('end_prop'):
                finished_matcher = matchers.pop()
                if matchers:
                    arg = next_arg.pop(matchers[-1])
                    matchers[-1].args[arg] = finished_matcher
                else:
                    self.matchers.append(finished_matcher)
            elif m.group('arg'):
                next_arg[matchers[-1]] = m.group('arg_name')
            elif m.group('str'):
                arg = next_arg.pop(matchers[-1])
                matchers[-1].args[arg] = m.group('str')[1:-1]
            elif m.group('error'):
                raise ValueError('Parse Error at character %s' %
                                 m.start())
            else:
                raise ValueError('Unexpected match')

    class PropMatcher(object):
        # todo: nested args!!
        def __init__(self, pred_type='.*', head='.*', **args):
            self.pred_type = pred_type
            self.head = head
            self.args = args

        def match(self, prop):
            if not re.match(self.pred_type, prop.pred_type.value):
                return False
            if not re.match(self.head, prop.head.text.lower()):
                return False
            for (role, arg_re) in self.args.items():
                for arg in prop.arguments:
                    if role == arg.role and re.match(arg_re, self.text_for(arg)):
                        break
                else:
                    return False
            return True

        def text_for(self, arg):
            if arg.syn_node: return arg.syn_node.text
            if arg.mention: return arg.mention.text
            if arg.proposition: return arg.proposition.head.text  # hmmm


###########################################################################
## All Pages
###########################################################################

def write_all_pages(html_files, out_dir, options):
    # Create the frames page.
    save(FRAMES_HTML, out_dir, 'index.html')

    save(BLANK_PAGE, out_dir, 'blank_page.html')

    nav_items = ''

    searchers = ([TermSearcher(filename, out_dir)
                  for filename in (options.term_search_files or ())] +
                 [PropSearcher(filename, out_dir)
                  for filename in (options.prop_search_files or ())])

    # Process each document.
    tuples = sorted(html_files.items())
    for index,(src_file,html_file) in enumerate(tuples):
        doc = Document(src_file)
        doc.filename = src_file
        doc.html_prefix = html_file[:-5].replace("#", "")

        # create mention->entity map; this is a bit of a hack.
        doc.mention_to_entity = dict((m, e) for e in doc.entity_set or ()
                                     for m in e.mentions)

        # Create the document-view page
        if options.show_doc_pages:
            logger.info('Processing %d of %d: %s...' % (index+1, len(tuples), doc.docid))
            write_document_pages(doc, out_dir, options)
            nav_items += doc_nav_to_html(doc, options.show_doc_entities, options.show_doc_graphs,
                                         options.show_merged_graphs)

        # Apply any searches.
        if searchers:
            logger.info('Searching %s...' % doc.docid)
            num_hits = 0
            for searcher in searchers:
                num_hits += searcher.update(doc)
            logger.info('Searching %d has hit(s)' % num_hits)


        if index and index % 5 == 0:
            logger.info('Writing partial index.html...')
            write_nav_page(nav_items, out_dir)
            logger.info('partial index.html written')


    for searcher in searchers:
        logger.info('Writing %s...' % searcher.html_name)
        searcher.write_pages()
        nav_items += searcher.nav_to_html()
        logger.info('%s written' % searcher.html_name)


    # Navigation page.
    logger.info('Writing index.html...')
    write_nav_page(nav_items, out_dir)
    logger.info('partial index.html written')





