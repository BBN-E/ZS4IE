from serif.xmlio import _AutoPopulatedXMLAttributeSpec


class metaSerifTheory(type):
    def __init__(cls, name, bases, dct):
        type.__init__(cls, name, bases, dct)
        # Register the class in a registry.
        cls.__theory_name__ = name
        if hasattr(cls, '__overrides__'):
            cls.__theory_name__ = cls.__overrides__
        # elif name in cls._theory_classes:
        #    print "Warning: overriding %s!" % name
        cls._theory_classes[cls.__theory_name__] = cls

        # Add an _auto_attribs attribute
        cls._auto_attribs = [
            (k, v) for (k, v) in list(dct.items())
            if isinstance(v, _AutoPopulatedXMLAttributeSpec)]
        for attr_name, attr_spec in cls._auto_attribs:
            attr_spec.__name__ = attr_name
        for base in bases:
            cls._auto_attribs.extend(getattr(base, '_auto_attribs', []))

        def sort_key(attrib):
            return (attrib[1]._attribute_number, attrib[0].lower())

        cls._auto_attribs.sort(key=sort_key)
