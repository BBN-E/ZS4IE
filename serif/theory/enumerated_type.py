######################################################################
# { Enumerated Type metaclass
######################################################################

class EnumeratedType(type):
    """
    >>> colors = EnumeratedType('colors', 'red green blue')
    >>> assert colors.red != colors.green
    >>> assert colors.red == colors.red
    """

    class _BaseClass(object):
        def __init__(self, value):
            self.__value = value
            self.__hash = hash(value)

        def __repr__(self):
            return '%s.%s' % (self.__class__.__name__, self.__value)

        def __hash__(self):
            return self.__hash

        def __eq__(self, other):
            if isinstance(other, self.__class__):
                return self.value == other.value
            return NotImplemented

        @property
        def value(self):
            return self.__value

    def __new__(cls, name, values):
        return type.__new__(cls, name, (cls._BaseClass,), {})

    def __init__(cls, name, values):
        if isinstance(values, str):
            values = values.split()
        cls.values = [cls(value) for value in values]
        for enum_name, enum_value in zip(values, cls.values):
            setattr(cls, enum_name, enum_value)

    def __iter__(self):
        return iter(self.values)

    def __len__(self):
        return len(self.values)

    def __getitem__(self, i):
        return self.values[i]

    def __repr__(self):
        return '<%s enumeration: %r>' % (self.__name__, tuple(self.values),)


######################################################################
# { Theory Objects Base Classes
######################################################################

# Define some enumerated types.
ParseType = EnumeratedType(
    'ParseType', 'full_parse np_chunk')
MentionType = EnumeratedType(
    'MentionType', 'none name pron desc part appo list nest')
PredType = EnumeratedType(
    'PredType', 'verb copula modifier noun poss loc set name pronoun comp dependency')
Genericity = EnumeratedType(
    'Genericity', 'Specific Generic')
Polarity = EnumeratedType(
    'Polarity', 'Positive Negative')
DirectionOfChange = EnumeratedType(
    'DirectionOfChange', 'Unspecified Increase Decrease')
Tense = EnumeratedType(
    'Tense', 'Unspecified Past Present Future')
Modality = EnumeratedType(
    'Modality', 'Asserted Other')
PropStatus = EnumeratedType(
    'PropStatus', 'Default If Future Negative Alleged Modal Unreliable')
Trend = EnumeratedType('Trend',"Increase Decrease Stable Unspecified")

