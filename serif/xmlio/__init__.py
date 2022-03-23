######################################################################
# { Theory Attribute Specifications
######################################################################

from xml.etree import ElementTree as ET


def escape_cdata_carriage_return(text, encoding='utf-8'):
    """
    Source copied from ElementTree.py and modified to add
    '\r' -> '&#xD;' replacement. Monkey patch!
    """
    # escape character data
    try:
        # it's worth avoiding do-nothing calls for strings that are
        # shorter than 500 character, or so.  assume that's, by far,
        # the most common case in most applications.
        if "&" in text:
            text = text.replace("&", "&amp;")
        if "<" in text:
            text = text.replace("<", "&lt;")
        if ">" in text:
            text = text.replace(">", "&gt;")
        if "\r" in text:
            text = text.replace("\r", "&#xD;")
        # Need to return a string, so after patching up the XML,
        # we need to decode it again...  I'm not convinced this
        # actually does anything.  I haven't found a counterexample
        # yet. -DJE
        return text.encode(encoding, "xmlcharrefreplace").decode(encoding)
    except (TypeError, AttributeError):
        ET._raise_serialization_error(text)


ET._escape_cdata = escape_cdata_carriage_return

SERIFXML_VERSION = 18

"""If true, then SerifTheory objects will keep a pointer to the
   ElementTree.Element that they were constructed from.  This
   makes it possible for the save() method to preserve any extra
   attributes or elements that were present in the original
   document."""
KEEP_ORIGINAL_ETREE = False


class _AutoPopulatedXMLAttributeSpec(object):
    """
    This is the abstract base class for \"Auto-populated XML attribute
    specifications\" (or AttributeSpec's for short).  Each
    AttributeSpec is used to define a single attribute for a Serif
    theory class.  Some examples of AttributeSpecs are::

        is_downcased = _SimpleAttribute(bool, default=False)
        sentences    = _ChildTheoryElement('Sentences')
        start_token  = _ReferenceAttribute('start_token', is_required=True)

    Each AttributeSpec defines a `set_value()` method, which is used
    to read the attribute's value from the XML input for a given
    theory object.  The default implementation of `set_value()` calls
    the abstract method `get_value()`, which should read the
    appropriate value from a given XML node, and stores it in the
    theory object (using `setattr`).

    The name of the instance variable that is used to store an
    attribute's value is always identical to the name of the class
    variable that holds the AttributeSpec.  For example, the Document
    class contains an AttributeSpec named 'docid'; and each instance
    of the Document class will have an instance variable with the same
    name ('docid') that is initialized by that AttributeSpec.  Note
    that this instance variable (containing the attribute value)
    shadows the class variable containing the AttributeSpec.
    """

    # We assign a unique attribute number to each AttributeSpec that
    # gets created.  This allows us to display attributes in the
    # correct order when pretty-printing.  (In particular, attributes
    # are displayed in the order in which they were defined.)
    attribute_counter = 0

    def __init__(self):
        self._attribute_number = self.attribute_counter
        _AutoPopulatedXMLAttributeSpec.attribute_counter += 1

    def set_value(self, etree, theory):
        """
        Set the value of this attribute.

        @param name: The name that should be used to store the attribute.
        @param etree: The (input) XML tree corresponding to `theory`.
        @param theory: The Serif theory object, to which the attribute
            should be added.
        """
        setattr(theory, self.__name__, self.get_value(etree, theory))

    def get_value(self, etree, theory):
        """
        Extract and return the value of this attribute from an input
        XML tree.

        @param name: The name that should be used to store the attribute.
        @param etree: The (input) XML tree corresponding to `theory`.
        @param theory: The Serif theory object, to which the attribute
            should be added.
        """
        raise AssertionError('get_value() is an abstract method.')

    def serialize(self, etree, theory, **options):
        raise AssertionError('serialize() is an abstract method.')

    def default_value(self):
        return None

    def help(self):
        """
        Return a single-line string describing this attribute
        """
        raise AssertionError('help() is an abstract method.')


class _SimpleAttribute(_AutoPopulatedXMLAttributeSpec):
    """
    A basic serif theory attribute, whose value is copied directly
    from a corresonding XML attribute.  The value should have a simple
    type (such as string, boolean, or integer).
    """

    def __init__(self, value_type=str, default=None, attr_name=None,
                 is_required=False):
        """
        @param value_type: The type of value expected for this attribute.
            This should be a Python type (such as int or bool), and is
            used directly to cast the string value to an appropriate value.
        @param default: The default value for this attribute.  I.e., if
            no value is provided, then the attribute will take this value.
            The default value is *not* required to be of the type specified
            by value_type -- in particular, the default may be None.
        @param attr_name: The name of the XML attribute used to store this
            value.  If not specified, then the name will default to the
            name of the serif theory attribute.
        @param is_required: If true, then raise an exception if this
            attribute is not defined on the XML input element.
        """
        _AutoPopulatedXMLAttributeSpec.__init__(self)
        self._value_type = value_type
        self._default = default
        self._attr_name = attr_name
        self._is_required = is_required

    def get_value(self, etree, theory):
        name = self._attr_name or self.__name__
        if name in etree.attrib:
            return self._parse_value(name, etree.attrib[name])
        elif self._is_required:
            raise ValueError('Attribute %s is required for %s' %
                             (name, etree))
        else:
            return self._default

    def _parse_value(self, name, value):
        if self._value_type == bool:
            if value.lower() == 'true': return True
            if value.lower() == 'false': return False
            raise ValueError('Attribute %s must have a boolean value '
                             '(either TRUE or FALSE)' % name)
        else:
            return self._value_type(value)

    def _encode_value(self, value):
        from serif.theory.enumerated_type import EnumeratedType
        if value is True:
            return 'TRUE'
        elif value is False:
            return 'FALSE'
        elif isinstance(value, bytes):
            return value.decode('utf-8')
        elif isinstance(value, EnumeratedType._BaseClass):
            return value.value
        elif not isinstance(value, str):
            return str(value)
        else:
            return value

    def serialize(self, etree, theory, **options):

        value = getattr(theory, self.__name__, None)
        explicit_defaults = options.get('explicit_defaults', True)
        if value is not None:
            if ((not explicit_defaults) and
                    (self._default is not None) and
                    (value == self._default)):
                return
            attr_name = self._attr_name or self.__name__
            value = self._encode_value(value)
            etree.attrib[attr_name] = value

    _HELP_TEMPLATE = 'a %s value extracted from the XML attribute %r'

    def help(self):
        name = self._attr_name or self.__name__
        s = self._HELP_TEMPLATE % (
            self._value_type.__name__, name)
        if self._is_required:
            s += ' (required)'
        else:
            s += ' (default=%r)' % self._default
        return s

    def default_value(self):
        return self._default

class _SimpleListAttribute(_SimpleAttribute):
    def _parse_value(self, name, value):
        return tuple(_SimpleAttribute._parse_value(self, name, v)
                     for v in value.split())

    def _encode_value(self, value):
        return ' '.join(_SimpleAttribute._encode_value(self, v)
                        for v in value)

    _HELP_TEMPLATE = 'a list of %s values extracted from the XML attribute %r'


class _IdAttribute(_AutoPopulatedXMLAttributeSpec):
    """
    An identifier attribute (copied from the XML attribute \"id\").
    In addtion to initializing theory.id, this attribute also
    registers the id in the identifier map that is owned by the
    theory's document.
    """

    def set_value(self, etree, theory):
        theory.id = etree.attrib.get('id')
        document = theory.document
        if document is None:
            raise ValueError('Containing document not found!')
        document.register_id(theory)

    def serialize(self, etree, theory, **options):
        xml_id = getattr(theory, 'id', None)
        if xml_id is not None:
            etree.attrib['id'] = xml_id

    def help(self):
        return "The XML id for this theory object (default=None)"


class _ReferenceAttribute(_SimpleAttribute):
    """
    An attribute that is used to point to another Serif theory object,
    using its identifier.  When this attribute is initialized, the
    target id is copied from the XML attribute with a specified name
    (`attr_name`), and stored as a private variable.  This id is *not*
    looked up during initialization, since its target may not have
    been created yet.

    Instead, this attribute uses a Python feature called
    \"descriptors\" to resolve the target id to a value when the
    attribute is accessed.

    In particular, each _ReferencedAttribute is a (non-data)
    descriptor on the Serif theory class, which means that its
    `__get__()` method is called whenever the corresponding Serif
    theory attribute is read.  The `__get__()` method looks up the
    target id in the identifier map that is owned by the theory's
    document.  If the identifier is found, then the corresponding
    theory object is returned; otherwise, a special `DanglingPointer`
    object is returned.
    """

    def __init__(self, attr_name, is_required=False, cls=None):
        """
        @param attr_name: The name of the XML idref attribute used to
            hold the pointer to a theory object.  Typically, these
            attribute names will end in '_id'.
        @param is_required: If true, then raise an exception if this
            attribute is not defined on the XML input element.  If
            is_required is false and the attribute is not defined on
            the XML input element, then the Serif theory attribute's
            value will be None.
        @param cls: The Serif theory class (or name of the class)
            that the target value should belong to.
        """
        self._attr_name = attr_name
        self._private_attr_name = '_' + attr_name
        self._cls = cls
        _SimpleAttribute.__init__(self, is_required=is_required,
                                  attr_name=attr_name)

    def set_value(self, etree, theory):
        # This stores the id, but does *not* look it up -- the target
        # for the pointer might not have been deserialized from xml yet.
        setattr(theory, self._private_attr_name,
                self.get_value(etree, theory))

    def serialize(self, etree, theory, **options):
        child = getattr(theory, self.__name__, None)
        if child is not None:
            etree.attrib[self._attr_name] = self._get_child_id(child)

    def _get_child_id(self, child):
        child_id = getattr(child, 'id', None)
        if child_id is None:
            raise ValueError('Serialization Error: attempt to serialize '
                             'a pointer to an object that has no id (%r)'
                             % child)
        return child_id

    def __get__(self, instance, owner=None):
        from serif.theory.serif_theory import SerifTheory
        # We look up the id only when the attribute is accessed.
        if instance is None: return self
        theory_id = getattr(instance, self._private_attr_name)
        if theory_id is None: return None
        document = instance.document
        if document is None:
            return DanglingPointer(theory_id)
        target = document.lookup_id(theory_id)
        if target is None:
            return DanglingPointer(theory_id)
        if self._cls is not None:
            if isinstance(self._cls, str):
                self._cls = SerifTheory._theory_classes[self._cls]
            if not isinstance(target, self._cls):
                raise ValueError('Expected %s to point to a %s' % (
                    self._attr_name, self._cls.__name__))
        return target

    def _cls_name(self):
        if self._cls is None:
            return 'theory object'
        elif isinstance(self._cls, str):
            return self._cls
        else:
            return self._cls.__name__

    def help(self):
        name = self._attr_name or self.__name__
        s = 'a pointer to a %s extracted from the XML attribute %r' % (
            self._cls_name(), name)
        if self._is_required: s += ' (required)'
        return s


class _ReferenceListAttribute(_ReferenceAttribute):
    """
    An attribute that is used to point to a sequence of Serif theory
    objects, using their identifiers.  This AttributeSpec is similar
    to `_ReferenceAttribute`, except that its value is a list of
    theory objects, rather than a single theory object.
    """

    def __get__(self, instance, owner=None):
        from serif.theory.serif_theory import SerifTheory
        theory_ids = getattr(instance, self._private_attr_name)
        theory_ids = (theory_ids or '').split()
        document = instance.document
        if document is None:
            return [DanglingPointer(tid) for tid in theory_ids]
        targets = [(document.lookup_id(tid) or DanglingPointer(tid))
                   for tid in theory_ids]
        if self._cls is not None:
            if isinstance(self._cls, str):
                self._cls = SerifTheory._theory_classes[self._cls]
            for t in targets:
                if not isinstance(t, (self._cls, DanglingPointer)):
                    raise ValueError('Expected %s to point to a %s; got a %s' % (
                        self._attr_name, self._cls.__name__, t.__class__.__name__))
        return targets

    def serialize(self, etree, theory, **options):
        child_ids = [self._get_child_id(child)
                     for child in getattr(theory, self.__name__, ())]
        if child_ids:
            etree.attrib[self._attr_name] = ' '.join(child_ids)

    def default_value(self):
        return []

    def help(self):
        name = self._attr_name or self.__name__
        s = ('a list of pointers to %ss extracted from '
             'the XML attribute %r' % (self._cls_name(), name))
        return s


class DanglingPointer(object):
    """
    A class used by `_ReferenceAttribute` to indicate that the target
    id has not yet been read.  In particular, a DanglingPointer will
    be returned by `ReferenceAttribute.__get__()` if a target pointer
    id is not found in the identifier map.
    """

    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return "<Dangling Pointer: id=%r>" % self.id

    def _get_summary(self):
        return "<Dangling Pointer: id=%r>" % self.id


class _OffsetAttribute(_AutoPopulatedXMLAttributeSpec):
    """
    An attribute used to store a start or end offset.  These
    attributes may be stored in the XML in two different ways: either
    using separate XML attributes for the begin and end offsets; or
    using a single XML attribute for both.  This AttributeSpec
    subclass is responsible for reading both formats.
    """

    def __init__(self, offset_side, offset_name, value_type=int):
        _AutoPopulatedXMLAttributeSpec.__init__(self)
        assert offset_side in ('start', 'end')
        self.is_start = (offset_side == 'start')
        self.offset_name = offset_name
        self.offset_attr = '%s_%s' % (offset_side, offset_name)
        self.condensed_offsets_attr = '%s_offsets' % offset_name
        self._value_type = value_type

    def get_value(self, etree, theory):
        if self.offset_attr in etree.attrib:
            return self._value_type(etree.attrib[self.offset_attr])
        elif self.condensed_offsets_attr in etree.attrib:
            s, e = etree.attrib[self.condensed_offsets_attr].split(':')
            if self.is_start:
                return self._value_type(s)
            else:
                return self._value_type(e)
        else:
            return None

    def serialize(self, etree, theory, **options):
        value = getattr(theory, self.__name__, None)
        if value is not None:
            if options.get('condensed_offsets', True):
                etree.attrib[self.condensed_offsets_attr] = '%s:%s' % (
                    getattr(theory, 'start_%s' % self.offset_name),
                    getattr(theory, 'end_%s' % self.offset_name))
            else:
                etree.attrib[self.offset_attr] = '%s' % value

    def help(self):
        return 'an offset extracted from XML attribute %r or %r' % (
            (self.offset_attr, self.condensed_offsets_attr))


class _ChildTheoryElement(_AutoPopulatedXMLAttributeSpec):
    """
    An attribute used to hold a child theory that is described in
    a child XML element.
    """

    def __init__(self, cls_name, is_required=False):
        """
        @param cls_name: The name of the Serif theory class for the
            child value.
        """
        _AutoPopulatedXMLAttributeSpec.__init__(self)
        self._is_required = is_required
        self._cls_name = cls_name

    def _get_child_elt(self, name, etree):
        if isinstance(name, tuple):
            elts = [elt for elt in etree if elt.tag in name]
            name = ' or '.join(name)  # for error messages.
        else:
            elts = [elt for elt in etree if elt.tag == name]
        if len(elts) == 1:
            return elts[0]
        elif len(elts) > 1:
            raise ValueError('Expected at most one %s' % name)
        elif self._is_required:
            raise ValueError('Expected exactly one %s' % name)
        else:
            return None

    def serialize(self, etree, theory, **options):
        child = getattr(theory, self.__name__, None)
        if child is not None:
            if (hasattr(child, '_etree') and child._etree in etree):
                child_etree = child.toxml(child._etree, **options)
            else:
                child_etree = child.toxml(**options)
                etree.append(child_etree)
            if isinstance(self._cls_name, tuple):
                assert child_etree.tag in self._cls_name
            else:
                assert child_etree.tag == self._cls_name

    def get_value(self, etree, theory):
        from serif.theory.serif_theory import SerifTheory
        name = self._cls_name or self.__name__
        child_elt = self._get_child_elt(name, etree)
        if child_elt is None:
            return None
        cls = SerifTheory._theory_classes.get(child_elt.tag)
        if cls is None:
            raise AssertionError('Theory class %s not defined!' % name)
        return cls(child_elt, theory)

    def help(self):
        s = 'a child %s theory' % self._cls_name
        if self._is_required:
            s += ' (required)'
        else:
            s += ' (optional)'
        return s


class _ChildTextElement(_ChildTheoryElement):
    """
    An attribute whose value should be extracted from the string text
    of a child XML element.  (c.f. _TextOfElement)
    """

    def set_text(self, text):
        self.text = text

    def get_value(self, etree, theory):
        child_elt = self._get_child_elt(self._cls_name, etree)
        if KEEP_ORIGINAL_ETREE:
            self._child_elt = child_elt
        if child_elt is None:
            return None
        else:
            return child_elt.text or ""

    def serialize(self, etree, theory, **options):
        text = getattr(theory, self.__name__, None)
        if text is not None:
            if hasattr(self, '_child_elt') and self._child_elt in etree:
                child_etree = self._child_elt
            else:
                del etree[:]
                child_etree = ET.Element(self._cls_name or self.__name__)
                etree.append(child_etree)
            child_etree.text = text
            child_etree.tail = '\n' + options.get('indent', '')

    def help(self):
        return 'a text string extracted from the XML element %r' % (
            self._cls_name)


class _TextOfElement(_AutoPopulatedXMLAttributeSpec):
    """
    An attribute whose value should be extracted from the string text
    of *this* XML element.  (c.f. _ChildTextElement)
    """

    def __init__(self, is_required=False, strip=False):
        _AutoPopulatedXMLAttributeSpec.__init__(self)
        self._strip = strip
        self._is_required = is_required

    def get_value(self, etree, theory):
        text = etree.text or ''
        if self._strip: text = text.strip()
        if self._is_required and not text:
            raise ValueError('Text content is required for %s' %
                             self.__name__)
        return text

    def serialize(self, etree, theory, **options):
        text = getattr(theory, self.__name__, None)
        if text is not None:
            # assert etree.text is None # only one text string!
            etree.text = text

    def help(self):
        return ("a text string extracted from this "
                "theory's XML element text")


class _ChildTheoryElementList(_AutoPopulatedXMLAttributeSpec):
    """
    An attribute whose value is a list of child theories.  Each child
    theory is deserialized from a single child XML element.
    """

    def __init__(self, cls_name, index_attrib=None):
        _AutoPopulatedXMLAttributeSpec.__init__(self)
        self._cls_name = cls_name
        self._index_attrib = index_attrib

    def get_value(self, etree, theory):
        from serif.theory.serif_theory import SerifTheory
        name = self._cls_name or self.__name__
        elts = [elt for elt in etree if elt.tag == name]
        cls = SerifTheory._theory_classes.get(name)
        if cls is None:
            raise AssertionError('Theory class %s not defined!' % name)
        result = [cls(elt, theory) for elt in elts]
        if self._index_attrib:
            for i, child in enumerate(result):
                child.__dict__[self._index_attrib] = i
        return result

    def serialize(self, etree, theory, **options):
        children = getattr(theory, self.__name__, ())
        if KEEP_ORIGINAL_ETREE:
            child_etrees = set(etree)
        else:
            child_etrees = set()
        for child in children:
            if (hasattr(child, '_etree') and child._etree in child_etrees):
                child_etree = child.toxml(child._etree, **options)
            else:
                child_etree = child.toxml(**options)
                etree.append(child_etree)
            assert child_etree.tag == self._cls_name

    def default_value(self):
        return []

    def help(self):
        s = 'a list of child %s theory objects' % self._cls_name
        return s
