def _truncate(text, maxlen):
    if text is None:
        return None
    elif len(text) <= maxlen:
        return text
    else:
        return text[:maxlen - 9] + '...' + text[-6:]


def _raise_expected_exactly_one_error(cls, single, multiple, n):
    raise ValueError(
        'The %(cls)s.%(single)s property can only be used if '
        'len(%(cls)s.%(multiple)s)==1.  For this instance, '
        'len(%(cls)s.%(multiple)s)==%(n)s.' % dict(
            cls=cls, single=single, multiple=multiple, n=n))
