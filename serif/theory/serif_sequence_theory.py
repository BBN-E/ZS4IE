import textwrap

from serif.theory.serif_theory import SerifTheory


class SerifSequenceTheory(SerifTheory):
    _children = "This class attr must be defined by subclasses."

    def __init__(self, *args, **kwargs):
        super(SerifSequenceTheory, self).__init__(*args, **kwargs)

    def __len__(self):
        return len(self._children)

    def __iter__(self):
        return self._children.__iter__()

    def __contains__(self, item):
        try:
            self.index(item)
            return True
        except ValueError as e:
            return False

    def __getitem__(self, n):
        return self._children.__getitem__(n)

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__theory_name__, self._children)

    def resolve_pointers(self, fail_on_dangling_pointer=True):
        SerifTheory.resolve_pointers(self, fail_on_dangling_pointer)
        for child in self._children:
            child.resolve_pointers(fail_on_dangling_pointer)

    @classmethod
    def _help_header(cls):
        child_class_name = cls._children._cls_name
        return textwrap.fill(
            'The %r class acts as a sequence of %r elements.  '
            'Additionally, it defines the following attributes:'
            % (cls.__theory_name__, child_class_name))

    def index(self, elem):
        return self._children.index(elem)
