from serif.theory.enumerated_type import ParseType
from serif.theory.nested_name_theory import NestedNameTheory
from serif.theory.np_chunk_theory import NPChunkTheory
from serif.theory.serif_theory import SerifTheory
from serif.xmlio import _ReferenceAttribute, _SimpleAttribute

from serif.theory.token_sequence import TokenSequence
from serif.theory.part_of_speech_sequence import PartOfSpeechSequence
from serif.theory.event_mention_set import EventMentionSet
from serif.theory.mention_set import MentionSet
from serif.theory.value_mention_set import ValueMentionSet
from serif.theory.name_theory import NameTheory
from serif.theory.parse import Parse
from serif.theory.proposition_set import PropositionSet
from serif.theory.dependency_set import DependencySet
from serif.theory.rel_mention_set import RelMentionSet
from serif.theory.actor_mention_set import ActorMentionSet


class SentenceTheory(SerifTheory):
    _token_sequence = _ReferenceAttribute('token_sequence_id',
                                          cls='TokenSequence')
    _pos_sequence = _ReferenceAttribute('part_of_speech_sequence_id',
                                        cls='PartOfSpeechSequence')
    _name_theory = _ReferenceAttribute('name_theory_id',
                                       cls='NameTheory')
    _nested_name_theory = _ReferenceAttribute('NestedNameTheory',
                                              cls='NestedNameTheory')
    _value_mention_set = _ReferenceAttribute('value_mention_set_id',
                                             cls='ValueMentionSet')
    _np_chunk_theory = _ReferenceAttribute('np_chunk_theory_id',
                                           cls='NPChunkTheory')
    _parse = _ReferenceAttribute('parse_id',
                                 cls='Parse')
    _mention_set = _ReferenceAttribute('mention_set_id',
                                       cls='MentionSet')
    _proposition_set = _ReferenceAttribute('proposition_set_id',
                                           cls='PropositionSet')
    _dependency_set = _ReferenceAttribute('dependency_set_id',
                                          cls='DependencySet')
    _rel_mention_set = _ReferenceAttribute('rel_mention_set_id',
                                           cls='RelMentionSet')
    _event_mention_set = _ReferenceAttribute('event_mention_set_id',
                                             cls='EventMentionSet')
    _actor_mention_set = _ReferenceAttribute('actor_mention_set_id',
                                             cls='ActorMentionSet')

    # If the following lines are uncommented,
    # then the 'primary_parse' field is added
    # to the output. -DJE
    primary_parse = _SimpleAttribute(ParseType,
                                     default=ParseType.full_parse)

    @classmethod
    def empty(cls, owner=None):
        ret = cls(owner=owner)
        return ret

    def _get_token_sequence(self):
        return self._token_sequence

    def _set_token_sequence(self, token_sequence):
        if not isinstance(token_sequence, TokenSequence):
            raise TypeError("TokenSequence")
        self._token_sequence = token_sequence

    token_sequence = property(_get_token_sequence, _set_token_sequence)

    def _get_pos_sequence(self):
        return self._pos_sequence

    def _set_pos_sequence(self, pos_sequence):
        if not isinstance(pos_sequence, PartOfSpeechSequence):
            raise TypeError("PartOfSpeechSequence")
        self._pos_sequence = pos_sequence

    pos_sequence = property(_get_pos_sequence, _set_pos_sequence)

    def _get_name_theory(self):
        return self._name_theory

    def _set_name_theory(self, name_theory):
        if not isinstance(name_theory, NameTheory):
            raise TypeError("NameTheory")
        self._name_theory = name_theory

    name_theory = property(_get_name_theory, _set_name_theory)

    def _get_nested_name_theory(self):
        return self._nested_name_theory

    def _set_nested_name_theory(self, nested_name_theory):
        if not isinstance(nested_name_theory, NestedNameTheory):
            raise TypeError("NestedNameTheory")
        self._nested_name_theory = nested_name_theory

    nested_name_theory = property(_get_nested_name_theory, _set_nested_name_theory)

    def _get_value_mention_set(self):
        return self._value_mention_set

    def _set_value_mention_set(self, value_mention_set):
        if not isinstance(value_mention_set, ValueMentionSet):
            raise TypeError("ValueMentionSet")
        self._value_mention_set = value_mention_set

    value_mention_set = property(_get_value_mention_set, _set_value_mention_set)

    def _get_np_chunk_theory(self):
        return self._np_chunk_theory

    def _set_np_chunk_theory(self, np_chunk_theory):
        if not isinstance(np_chunk_theory, NPChunkTheory):
            raise TypeError("NPChunkTheory")
        self._np_chunk_theory = np_chunk_theory

    np_chunk_theory = property(_get_np_chunk_theory, _set_np_chunk_theory)

    def _get_parse(self):
        return self._parse

    def _set_parse(self, parse):
        if not isinstance(parse, Parse):
            raise TypeError("Parse")
        self._parse = parse

    parse = property(_get_parse, _set_parse)

    def _get_mention_set(self):
        return self._mention_set

    def _set_mention_set(self, mention_set):
        if not isinstance(mention_set, MentionSet):
            raise TypeError("MentionSet")
        self._mention_set = mention_set

    mention_set = property(_get_mention_set, _set_mention_set)

    def _get_proposition_set(self):
        return self._proposition_set

    def _set_proposition_set(self, proposition_set):
        if not isinstance(proposition_set, PropositionSet):
            raise TypeError("PropositionSet")
        self._proposition_set = proposition_set

    proposition_set = property(_get_proposition_set, _set_proposition_set)

    def _get_dependency_set(self):
        return self._dependency_set

    def _set_dependency_set(self, dependency_set):
        if not isinstance(dependency_set, DependencySet):
            raise TypeError("DependencySet")
        self._dependency_set = dependency_set

    dependency_set = property(_get_dependency_set, _set_dependency_set)

    def _get_rel_mention_set(self):
        return self._rel_mention_set

    def _set_rel_mention_set(self, rel_mention_set):
        if not isinstance(rel_mention_set, RelMentionSet):
            raise TypeError("RelMentionSet")
        self._rel_mention_set = rel_mention_set

    rel_mention_set = property(_get_rel_mention_set, _set_rel_mention_set)

    def _get_event_mention_set(self):
        return self._event_mention_set

    def _set_event_mention_set(self, event_mention_set):
        if not isinstance(event_mention_set, EventMentionSet):
            raise TypeError("EventMentionSet")
        self._event_mention_set = event_mention_set

    event_mention_set = property(_get_event_mention_set, _set_event_mention_set)

    def _get_actor_mention_set(self):
        return self._actor_mention_set

    def _set_actor_mention_set(self, actor_mention_set):
        if not isinstance(actor_mention_set, ActorMentionSet):
            raise TypeError("ActorMentionSet")
        self._actor_mention_set = actor_mention_set

    actor_mention_set = property(_get_actor_mention_set, _set_actor_mention_set)
