from serif.theory.event_mention_set import EventMentionSet
from serif.theory.mention_set import MentionSet
from serif.theory.value_mention_set import ValueMentionSet
from serif.theory.name_theory import NameTheory
from serif.theory.parse import Parse
from serif.theory.proposition_set import PropositionSet
from serif.theory.dependency_set import DependencySet
from serif.theory.region import Region
from serif.theory.rel_mention_set import RelMentionSet
from serif.theory.serif_sentence_theory import SerifSentenceTheory
from serif.theory.sentence_theory import SentenceTheory
from serif.theory.token_sequence import TokenSequence
from serif.theory.part_of_speech_sequence import PartOfSpeechSequence
from serif.theory.actor_mention_set import ActorMentionSet
from serif.xmlio import _ReferenceAttribute, _SimpleAttribute, _ChildTextElement, _ChildTheoryElement, \
    _ChildTheoryElementList

class Sentence(SerifSentenceTheory):
    region = _ReferenceAttribute('region_id', cls=Region,
                                  is_required=True)
    is_annotated = _SimpleAttribute(bool, default=True)
    contents = _ChildTextElement('Contents')
    _token_sequences = _ChildTheoryElementList('TokenSequence')
    _pos_sequences = _ChildTheoryElementList('PartOfSpeechSequence')
    _name_theories = _ChildTheoryElementList('NameTheory')
    _nested_name_theories = _ChildTheoryElementList('NestedNameTheory')
    _value_mention_sets = _ChildTheoryElementList('ValueMentionSet')
    _np_chunk_theories = _ChildTheoryElementList('NPChunkTheory')
    _parses = _ChildTheoryElementList('Parse')
    _mention_sets = _ChildTheoryElementList('MentionSet')
    _proposition_sets = _ChildTheoryElementList('PropositionSet')
    _dependency_sets = _ChildTheoryElementList('DependencySet')
    _rel_mention_sets = _ChildTheoryElementList('RelMentionSet')
    _event_mention_sets = _ChildTheoryElementList('EventMentionSet')
    _actor_mention_sets = _ChildTheoryElementList('ActorMentionSet')

    _sentence_theories = _ChildTheoryElementList('SentenceTheory')

    # n.b.: "parse" and "sentence_theory" are defined as properties.

    @classmethod
    def from_values(cls, owner=None, start_char=0, end_char=0, region=None, is_annotated=True):
        ret = cls(owner=owner)
        ret.set_offset(start_char, end_char)
        ret.set_region_id(region)
        ret.set_is_annotated(is_annotated)
        st = SentenceTheory(owner=ret)
        st.document.generate_id(st)
        ret._set_sentence_theory(st)
        return ret

    def set_region_id(self, region_id):
        self.region = region_id
        
    def set_is_annotated(self, is_annotated):
        self.is_annotated = is_annotated

    def update_sentence_theories(self, field, obj):
        for st in self._sentence_theories:
            setattr(st, field, obj)
        
    def add_new_sentence_theory(self):
        sentence_theory = SentenceTheory.empty(owner=self)
        sentence_theory.document.generate_id(sentence_theory)
        self._sentence_theories.append(sentence_theory)
        return sentence_theory
    
    @property 
    def sentence_theories(self):
        return self._sentence_theories
        
    @property
    def token_sequence(self):
        """If there is a single SentenceTheory for this Sentence, 
           this will return the TokenSequence for that SentenceTheory. 
           Otherwise, it will raise an exception.
        """
        return self.sentence_theory.token_sequence

    def add_new_token_sequence(self, sentence_theory=None):
        if sentence_theory is None:
            sentence_theory = self.sentence_theory
        token_sequence = TokenSequence.empty(owner=self)
        token_sequence.document.generate_id(token_sequence)
        self._token_sequences.append(token_sequence)
        sentence_theory.token_sequence = token_sequence
        return token_sequence

    def add_new_part_of_speech_sequence(self, sentence_theory=None):
        if sentence_theory is None:
            sentence_theory = self.sentence_theory
        part_of_speech_sequence = PartOfSpeechSequence.empty(
            owner=self, token_sequence=sentence_theory.token_sequence)
        part_of_speech_sequence.document.generate_id(part_of_speech_sequence)
        self._pos_sequences.append(part_of_speech_sequence)
        sentence_theory.pos_sequence = part_of_speech_sequence
        return part_of_speech_sequence

    @property
    def pos_sequence(self):
        """If there is a single SentenceTheory for this Sentence, 
           this will return the PartOfSpeechSequence for that SentenceTheory. 
           Otherwise, it will raise an exception.
        """
        return self.sentence_theory.pos_sequence


    @property
    def name_theory(self):
        """If there is a single SentenceTheory for this Sentence, 
           this will return the NameTheory for that SentenceTheory. 
           Otherwise, it will raise an exception.
        """
        return self.sentence_theory.name_theory

    def add_new_name_theory(self, sentence_theory=None):
        if sentence_theory is None:
            sentence_theory = self.sentence_theory
        name_theory = NameTheory.empty(
            owner=self, token_sequence=sentence_theory.token_sequence)
        name_theory.document.generate_id(name_theory)
        self._name_theories.append(name_theory)
        sentence_theory.name_theory = name_theory
        return name_theory

    @property
    def nested_name_theory(self):
        """If there is a single SentenceTheory for this Sentence, 
           this will return the NestedNameTheory for that SentenceTheory. 
           Otherwise, it will raise an exception.
        """
        return self.sentence_theory.nested_name_theory
        
    @property
    def value_mention_set(self):
        """If there is a single SentenceTheory for this Sentence, 
           this will return the ValueMentionSet for that SentenceTheory. 
           Otherwise, it will raise an exception.
        """
        return self.sentence_theory.value_mention_set

    def add_new_value_mention_set(self, sentence_theory=None):
        if sentence_theory is None:
            sentence_theory = self.sentence_theory
        value_mention_set = ValueMentionSet.empty(
            owner=self, token_sequence=sentence_theory.token_sequence)
        value_mention_set.document.generate_id(value_mention_set)
        self._value_mention_sets.append(value_mention_set)
        sentence_theory.value_mention_set = value_mention_set
        return value_mention_set

    @property
    def np_chunk_theory(self):
        """If there is a single SentenceTheory for this Sentence, 
           this will return the NPChunkTheory for that SentenceTheory. 
           Otherwise, it will raise an exception.
        """
        return self.sentence_theory.np_chunk_theory
        
    @property
    def parse(self):
        """If there is a single SentenceTheory for this Sentence, 
           this will return the Parse for that SentenceTheory. 
           Otherwise, it will raise an exception.
        """
        return self.sentence_theory.parse

    def add_new_parse(
        self, score, token_sequence, treebank_string, sentence_theory=None):
        if sentence_theory is None:
            sentence_theory = self.sentence_theory
        # from_values calls generate_id which is different from other
        # objects. This is a consequence of needing to have the ID when
        # creating the SynNode objects from the treebank string.
        parse = Parse.from_values(
            owner=self, score=score, token_sequence=token_sequence,
            treebank_string=treebank_string)
        self._parses.append(parse)
        sentence_theory.parse = parse
        return parse

    @property
    def mention_set(self):
        """If there is a single SentenceTheory for this Sentence, 
           this will return the MentionSet for that SentenceTheory. 
           Otherwise, it will raise an exception.
        """
        return self.sentence_theory.mention_set

    def add_new_mention_set(self, sentence_theory=None):
        if sentence_theory is None:
            sentence_theory = self.sentence_theory
        mention_set = MentionSet.empty(
            owner=self, parse=sentence_theory.parse)
        mention_set.document.generate_id(mention_set)
        self._mention_sets.append(mention_set)
        sentence_theory.mention_set = mention_set
        return mention_set
        
    @property
    def proposition_set(self):
        """If there is a single SentenceTheory for this Sentence, 
           this will return the PropositionSet for that SentenceTheory. 
           Otherwise, it will raise an exception.
        """
        return self.sentence_theory.proposition_set

    def add_new_proposition_set(self, mention_set, sentence_theory=None):
        if sentence_theory is None:
            sentence_theory = self.sentence_theory
        proposition_set = PropositionSet.empty(
            owner=self, mention_set = mention_set)
        proposition_set.document.generate_id(proposition_set)
        self._proposition_sets.append(proposition_set)
        sentence_theory.proposition_set = proposition_set
        return proposition_set

    @property
    def dependency_set(self):
        """If there is a single SentenceTheory for this Sentence, 
           this will return the DependencySet for that SentenceTheory. 
           Otherwise, it will raise an exception.
        """
        return self.sentence_theory.dependency_set
    
    def add_new_dependency_set(self, mention_set, sentence_theory=None):
        if sentence_theory is None:
            sentence_theory = self.sentence_theory
        dependency_set = DependencySet.empty(
            owner=self, mention_set=mention_set)
        dependency_set.document.generate_id(dependency_set)
        self._dependency_sets.append(dependency_set)
        sentence_theory.dependency_set = dependency_set
        return dependency_set

    @property
    def rel_mention_set(self):
        """If there is a single SentenceTheory for this Sentence, 
           this will return the RelMentionSet for that SentenceTheory. 
           Otherwise, it will raise an exception.
        """
        return self.sentence_theory.rel_mention_set

    def add_new_relation_mention_set(self, sentence_theory=None):
        if sentence_theory is None:
            sentence_theory = self.sentence_theory
        rel_mention_set = RelMentionSet.empty(owner=self)
        rel_mention_set.document.generate_id(rel_mention_set)
        self._rel_mention_sets.append(rel_mention_set)
        sentence_theory.rel_mention_set = rel_mention_set
        return rel_mention_set

    @property
    def event_mention_set(self):
        """If there is a single SentenceTheory for this Sentence, 
           this will return the EventMentionSet for that SentenceTheory. 
           Otherwise, it will raise an exception.
        """
        return self.sentence_theory.event_mention_set

    def add_new_event_mention_set(self, sentence_theory=None):
        if sentence_theory is None:
            sentence_theory = self.sentence_theory
        event_mention_set = EventMentionSet.empty(
            owner=self, parse=sentence_theory.parse)
        event_mention_set.document.generate_id(event_mention_set)
        self._event_mention_sets.append(event_mention_set)
        sentence_theory.event_mention_set = event_mention_set
        return event_mention_set

    @property
    def actor_mention_set(self):
        """If there is a single SentenceTheory for this Sentence, 
           this will return the ActorMentionSet for that SentenceTheory. 
           Otherwise, it will raise an exception.
        """
        return self.sentence_theory.actor_mention_set

    def add_new_actor_mention_set(self, sentence_theory=None):
        if sentence_theory is None:
            sentence_theory = self.sentence_theory
        actor_mention_set = ActorMentionSet.empty(owner=self)
        actor_mention_set.document.generate_id(actor_mention_set)
        self._actor_mention_sets.append(actor_mention_set)
        sentence_theory.actor_mention_set = actor_mention_set
        return actor_mention_set
