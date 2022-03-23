import textwrap
import weakref

from serif.theory.meta_serif_theory import metaSerifTheory
from serif.util import _truncate
from serif.xmlio import _IdAttribute, KEEP_ORIGINAL_ETREE, ET, _ReferenceAttribute, DanglingPointer


class SerifTheory(object, metaclass=metaSerifTheory):
    """
    The base class for serif theory types.
    """
    _theory_classes = {}

    # Every theory object may take an id.
    id = _IdAttribute()

    _OWNER_IS_REQUIRED = True

    def __init__(self, etree=None, owner=None, **attribs):
        # Set our owner pointer.
        if owner is not None:
            self._owner = weakref.ref(owner)
        elif self._OWNER_IS_REQUIRED:
            raise ValueError('%s constructor requires an owner' %
                             self.__class__.__name__)
        else:
            self._owner = None
        # Intialize, either from etree or from attributes.
        if etree is not None:
            if attribs:
                raise ValueError('Specify etree or attribs, not both!')
            self._init_from_etree(etree, owner)
        else:
            for attr_name, attr_spec in self._auto_attribs:
                value = attribs.pop(attr_name, None)
                if value is not None:
                    setattr(self, attr_name, value)
                else:
                    setattr(self, attr_name, attr_spec.default_value())

    def _init_from_etree(self, etree, owner):
        assert etree is not None
        if etree.tag != self.__class__.__theory_name__:
            raise ValueError('Expected a %s, got a %s!' %
                             (self.__class__.__theory_name__, etree.tag))
        if KEEP_ORIGINAL_ETREE:
            self._etree = etree
        # Fill in any attribute values
        for name, attr in self._auto_attribs:
            attr.set_value(etree, self)

    def toxml(self, etree=None, **options):
        """
        If `etree` is specified, then this theory object will be
        serialized into that element tree Element; otherwise, a new
        Element will be created.
        """
        # print 'serializing %s' % self.__class__.__theory_name__
        indent = options.get('indent')
        if indent is not None: options['indent'] += '  '

        if etree is None:
            etree = ET.Element(self.__class__.__theory_name__)
        else:
            assert etree.tag == self.__class__.__theory_name__, (
                etree.tag, self.__class__.__theory_name__)

        for name, attr in self._auto_attribs:
            attr.serialize(etree, self, **options)

        # Indentation...
        if len(etree) > 0 and indent is not None:
            etree.text = '\n' + indent + '  '
            for child in etree[:-1]:
                child.tail = '\n' + indent + '  '
            etree[-1].tail = '\n' + indent
        if indent is not None: options['indent'] = indent
        etree.tail = '\n'
        return etree

    def pprint(self, depth=-1, hide=(), follow_pointers=False,
               indent='  ', memo=None):
        """
        Return a pretty-printed string representation of this SERIF
        theory object.  The first line identifies this theory object,
        and the subsequent lines describe its contents (including
        nested or referenced theory objects).

        @param depth: The maximum depth to which nested theory objects
            should be displayed.
        @param hide: A set of names of attributes that should not
            be displayed.  (By default, the XML id and the EDT and
            byte offsets are not displayed by __str__).
        @param follow_pointers: If true, then attributes that contain
            pointers have their contents displayed just like nested
            elements.  If false, then the pointer targets are not
            expanded.
        """
        if memo is None: memo = set()
        if id(self) in memo:
            return '<%s...>' % self.__class__.__theory_name__
        memo.add(id(self))
        s = self._pprint_firstline(indent)
        for attr_name, attr_spec in self.__class__._auto_attribs:
            if attr_name in hide: continue
            val = getattr(self, attr_name)
            if attr_name == '_children':
                attr_name = ''
            elif attr_name.startswith('_'):
                continue
            attr_depth = depth
            if (not follow_pointers and val is not None and
                    isinstance(attr_spec, _ReferenceAttribute)
                    and not isinstance(val, DanglingPointer)):
                s += '\n%s%s = <%s...>' % (
                    indent, attr_name, getattr(val.__class__, '__theory_name__',
                                               val.__class__.__name__))
            else:
                s += '\n' + self._pprint_value(attr_name, val, attr_depth, hide,
                                               follow_pointers, indent, memo)
        return s

    def _get_summary(self):
        return None

    def _pprint_firstline(self, indent):
        s = self.__class__.__theory_name__ + ':'
        text = self._get_summary()
        if text:
            maxlen = max(9, 65 - len(indent) -
                         len(self.__class__.__theory_name__) * 2)
            s += ' %s' % _truncate(text, maxlen)
        return s

    def _pprint_value(self, attr, val, depth, hide,
                      follow_pointers, indent, memo):
        s = indent
        if attr: s += attr + ' = '
        if isinstance(val, SerifTheory):
            if depth is not None and depth == 0:
                return s + '<%s...>' % getattr(val.__class__, '__theory_name__',
                                               val.__class__.__name__)
            return s + val.pprint(depth - 1, hide, follow_pointers,
                                  indent + '  ', memo)
        elif isinstance(val, list):
            if len(val) == 0: return s + '[]'
            if depth is not None and depth == 0: return s + '[...]'
            items = [self._pprint_value('', item, depth - 1, hide,
                                        follow_pointers, indent + '  ', memo)
                     for item in val]
            if depth == 1 and len(items) > 12:
                items = items[:10] + ['%s  ...and %d more...' %
                                      (indent, len(items) - 10)]
            s += '[\n%s\n%s]' % ('\n'.join(items), indent)
            return s
        elif isinstance(val, str):
            text = repr(val)
            maxlen = max(9, 75 - len(s))
            if len(text) > maxlen:
                text = text[:maxlen - 9] + '...' + text[-6:]
            return s + text
        else:
            return s + repr(val)

    _default_hidden_attrs = {'id', 'start_byte', 'end_byte',
                                 'start_edt', 'end_edt'}

    def __repr__(self):
        text = self._get_summary()
        if text:
            return '<%s %s>' % (self.__class__.__theory_name__, text)
        else:
            return '<%s>' % self.__class__.__theory_name__

    def __str__(self):
        return self.pprint(depth=2, hide=self._default_hidden_attrs,
                           follow_pointers=False)

    @property
    def owner(self):
        """The theory object that owns this SerifTheory"""
        if self._owner is None:
            return None
        else:
            return self._owner()

    def owner_with_type(self, theory_class):
        """
        Find and return the closest owning theory with the given
        class.  If none is found, return None.  E.g., use
        tok.owner(Sentence) to find the sentence containing a token.
        """
        if isinstance(theory_class, str):
            theory_class = SerifTheory._theory_classes[theory_class]
        theory = self
        while theory is not None and not isinstance(theory, theory_class):
            if theory._owner is None: return None
            theory = theory._owner()
        return theory

    @property
    def document(self):
        """The document that contains this SerifTheory"""
        return self.owner_with_type("Document")

    @property
    def sentence(self):
        return self.owner_with_type("Sentence")

    def get_original_text_substring(self, start_char, end_char):
        """
        Return the original text substring spanning from start_char to
        end_char.  If this theory is contained in a sentence, then the
        string is taken from that sentence's contents string (if defined);
        otherwise, it is taken from the document's original text string.
        """
        if start_char is None or end_char is None:
            return None

        from serif.theory.document import Document
        from serif.theory.original_text import OriginalText
        theory = self
        while theory is not None:
            if isinstance(theory, OriginalText):
                s = theory.start_char
                return theory.contents[start_char - s:end_char - s + 1]
            elif isinstance(theory, Document):
                theory = theory.original_text
            else:
                theory = theory.owner
        return None

    def resolve_pointers(self, fail_on_dangling_pointer=True):
        """
        Replace reference attributes with their actual values for this
        theory and any theory owned by this theory (directly or
        indirectly).  Prior to calling this, every time you access a
        reference attribute, its value will be looked up in the
        document's identifier map.

        @param fail_on_dangling_pointer: If true, then raise an exception
        if we find a dangling pointer.
        """
        for attr_name, attr_spec in self._auto_attribs:
            attr_val = getattr(self, attr_name)
            # Replace any reference attribute w/ its actual value (unless
            # it's a dangling pointer)
            if isinstance(attr_spec, _ReferenceAttribute):
                if attr_name not in self.__dict__:
                    if not isinstance(attr_val, DanglingPointer):
                        setattr(self, attr_name, attr_val)
                    elif fail_on_dangling_pointer:
                        raise ValueError('Dangling pointer: %r' % attr_val)

            # Recurse to any owned objects.
            elif isinstance(attr_val, SerifTheory):
                attr_val.resolve_pointers(fail_on_dangling_pointer)

    @classmethod
    def _help_header(cls):
        return 'The %r class defines the following attributes:' % (
            cls.__theory_name__)

    @classmethod
    def help(cls):
        props = [(k, v) for base in cls.mro()
                 for (k, v) in list(base.__dict__.items())
                 if isinstance(v, property)]

        s = cls._help_header() + '\n'
        w = max([8] + [len(n) for (n, c) in cls._auto_attribs] +
                [len(n) for (n, p) in props]) + 2
        for attr_name, attr_spec in cls._auto_attribs:
            if attr_name == '_children': continue
            help_line = textwrap.fill(attr_spec.help(),
                                      initial_indent=' ' * (w + 3),
                                      subsequent_indent=' ' * (w + 3)).strip()
            s += '  %s %s\n' % (attr_name.ljust(w, '.'), help_line)
        if props:
            s += ('The following derived properties are also '
                  'available as attributes:\n')
            for (k, v) in props:
                help_text = v.__doc__ or '(undocumented)'
                help_text = help_text.replace(
                    'this SerifTheory', 'this ' + cls.__theory_name__)
                help_text = ' '.join(help_text.split())
                help_line = textwrap.fill(
                    help_text,
                    initial_indent=' ' * (w + 3),
                    subsequent_indent=' ' * (w + 3)).strip()
                s += '  %s %s\n' % (k.ljust(w, '.'), help_line)
        # s += '  %s %s\n' % ('owner'.ljust(w, '.'),
        #                     'The theory object that owns this %s' %
        #                     cls.__theory_name__)
        # s += '  %s %s\n' % ('document'.ljust(w, '.'),
        #                     'The Document that contains this %s' %
        #                     cls.__theory_name__)
        print(s.rstrip())

