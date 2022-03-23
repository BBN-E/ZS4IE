import logging

logger = logging.getLogger(__name__)

from serif.theory.serif_document_theory import SerifDocumentTheory
from serif.xmlio import _SimpleAttribute, _ChildTheoryElement


from serif.theory.actor_entity import ActorEntity
from serif.theory.actor_entity_set import ActorEntitySet
from serif.theory.actor_mention import ActorMention
from serif.theory.actor_mention_set import ActorMentionSet
from serif.theory.actor_mention_theory import ActorMentionTheory
from serif.theory.alternate_pos import AlternatePOS
from serif.theory.argument import Argument
from serif.theory.attribute import Attribute
from serif.theory.date_time import DateTime
from serif.theory.default_country_actor import DefaultCountryActor
from serif.theory.document_actor_info import DocumentActorInfo
from serif.theory.entity import Entity
from serif.theory.entity_set import EntitySet
from serif.theory.enumerated_type import ParseType,MentionType,PredType,Genericity,Polarity,DirectionOfChange,Tense,Modality,PropStatus,Trend
from serif.theory.event import Event
from serif.theory.event_arg import EventArg
from serif.theory.event_event_relation_mention import EventEventRelationMention
from serif.theory.event_event_relation_mention_set import EventEventRelationMentionSet
from serif.theory.event_mention import EventMention
from serif.theory.event_mention_anchor import EventMentionAnchor
from serif.theory.event_mention_arg import EventMentionArg
from serif.theory.event_mention_factor_type import EventMentionFactorType
from serif.theory.event_mention_relation_argument import EventMentionRelationArgument
from serif.theory.event_mention_set import EventMentionSet
from serif.theory.event_set import EventSet
from serif.theory.fact import Fact
from serif.theory.fact_argument import FactArgument
from serif.theory.fact_set import FactSet
from serif.theory.field import Field
from serif.theory.entry import Entry
from serif.theory.flexible_event_mention import FlexibleEventMention
from serif.theory.flexible_event_mention_arg import FlexibleEventMentionArg
from serif.theory.flexible_event_mention_set import FlexibleEventMentionSet
from serif.theory.icews_actor_mention_set import ICEWSActorMentionSet
from serif.theory.icews_event_mention import ICEWSEventMention
from serif.theory.icews_event_mention_relation_argument import ICEWSEventMentionRelationArgument
from serif.theory.icews_event_mention_set import ICEWSEventMentionSet
from serif.theory.icews_event_participant import ICEWSEventParticipant
from serif.theory.icews_event_participant_theory import ICEWSEventParticipantTheory
from serif.theory.lexical_entry import LexicalEntry
from serif.theory.lexicon import Lexicon
from serif.theory.mention import Mention
from serif.theory.mention_fact_argument import MentionFactArgument
from serif.theory.mention_set import MentionSet
from serif.theory.metadata import Metadata
from serif.theory.modal_temporal_relation_mention import ModalTemporalRelationMention
from serif.theory.modal_temporal_relation_argument import ModalTemporalRelationArgument
from serif.theory.modal_temporal_relation_mention_set import ModalTemporalRelationMentionSet
from serif.theory.name import Name
from serif.theory.name_theory import NameTheory
from serif.theory.nested_name import NestedName
from serif.theory.nested_name_theory import NestedNameTheory
from serif.theory.np_chunk import NPChunk
from serif.theory.np_chunk_theory import NPChunkTheory
from serif.theory.original_text import OriginalText
from serif.theory.parse import Parse
from serif.theory.part_of_speech_sequence import PartOfSpeechSequence
from serif.theory.pos import POS
from serif.theory.proposition import Proposition
from serif.theory.proposition_set import PropositionSet
from serif.theory.region import Region
from serif.theory.regions import Regions
from serif.theory.rel_mention import RelMention
from serif.theory.rel_mention_set import RelMentionSet
from serif.theory.relation import Relation
from serif.theory.relation_argument import RelationArgument
from serif.theory.relation_set import RelationSet
from serif.theory.actor_entity_set import ActorEntitySet
from serif.theory.segment import Segment
from serif.theory.segments import Segments
from serif.theory.sentence import Sentence
from serif.theory.sentence_theory import SentenceTheory
from serif.theory.sentences import Sentences
from serif.theory.span import Span
from serif.theory.string_fact_argument import StringFactArgument
from serif.theory.syn_node import SynNode
from serif.theory.text_span_fact_argument import TextSpanFactArgument
from serif.theory.timex2 import Timex2
from serif.theory.token import Token
from serif.theory.token_sequence import TokenSequence
from serif.theory.ut_coref import UTCoref
from serif.theory.value import Value
from serif.theory.value_mention import ValueMention
from serif.theory.value_mention_fact_argument import ValueMentionFactArgument
from serif.theory.value_mention_set import ValueMentionSet
from serif.theory.value_set import ValueSet

class Document(SerifDocumentTheory):

    docid = _SimpleAttribute(is_required=True)
    language = _SimpleAttribute(is_required=True)
    source_type = _SimpleAttribute(default='UNKNOWN')
    is_downcased = _SimpleAttribute(bool, default=False)
    document_time_start = _SimpleAttribute()
    document_time_end = _SimpleAttribute()
    original_text = _ChildTheoryElement('OriginalText')
    date_time = _ChildTheoryElement('DateTime')
    regions = _ChildTheoryElement('Regions')
    segments = _ChildTheoryElement('Segments')
    metadata = _ChildTheoryElement('Metadata')
    sentences = _ChildTheoryElement('Sentences')
    entity_set = _ChildTheoryElement('EntitySet')
    value_set = _ChildTheoryElement('ValueSet')
    relation_set = _ChildTheoryElement('RelationSet')
    event_set = _ChildTheoryElement('EventSet')
    value_mention_set = _ChildTheoryElement('ValueMentionSet')
    utcoref = _ChildTheoryElement('UTCoref')
    rel_mention_set = _ChildTheoryElement('RelMentionSet')
    lexicon = _ChildTheoryElement('Lexicon')
    actor_entity_set = _ChildTheoryElement('ActorEntitySet')
    actor_mention_set = _ChildTheoryElement('ActorMentionSet')
    document_actor_info = _ChildTheoryElement('DocumentActorInfo')
    fact_set = _ChildTheoryElement('FactSet')
    icews_actor_mention_set = _ChildTheoryElement('ICEWSActorMentionSet')
    icews_event_mention_set = _ChildTheoryElement('ICEWSEventMentionSet')
    flexible_event_mention_set = _ChildTheoryElement('FlexibleEventMentionSet')
    event_event_relation_mention_set = _ChildTheoryElement('EventEventRelationMentionSet')
    modal_temporal_relation_mention_set = _ChildTheoryElement('ModalTemporalRelationMentionSet')

    def construct_original_text(self, text,
                                start_char, end_char):
        from serif.theory.original_text import OriginalText
        original_text = OriginalText.from_values(start_char=start_char, end_char=end_char, text=text, owner=self)
        original_text.document.generate_id(original_text)
        # original_text.contents = ET.Element("Contents")
        # original_text.contents.text = text
        self.original_text = original_text

    def construct_date_time(self, start_char, end_char):
        from serif.theory.date_time import DateTime
        date_time = DateTime.from_values(start_char=start_char, end_char=end_char, owner=self)
        date_time.document.generate_id(date_time)
        self.date_time = date_time

        # date_time = ET.Element("Contents")
        # date_time.set("char_offsets",)

    def construct_regions(self, start_char, end_char, tag=None):
        from serif.theory.regions import Regions
        from serif.theory.region import Region
        regions = Regions(owner=self)
        region = Region.from_values(owner=regions, start_char=start_char, end_char=end_char, tag=tag)
        region.document.generate_id(region)
        regions.add_region(region)
        self.regions = regions

    def construct_segments(self):
        from serif.theory.segments import Segments
        segments = Segments(owner=self)
        self.segments = segments

    def construct_metadata(self, start_char=None, end_char=None, span_type=None, region_type=None):
        from serif.theory.metadata import Metadata
        from serif.theory.span import Span
        metadata = Metadata(owner=self)
        if start_char is not None and end_char is not None:
            span = Span.from_values(owner=metadata, start_char=start_char, end_char=end_char, span_type=span_type,
                                    region_type=region_type)
            span.document.generate_id(span)
            metadata.add_span(span)
        self.metadata = metadata

    def add_event_event_relation_mention_set(self, evt_evt_rel_mention_set):
        self.event_event_relation_mention_set = evt_evt_rel_mention_set

    def add_modal_temporal_relation_mention_set(self, mod_tmp_rel_mention_set):
        self.modal_temporal_relation_mention_set = mod_tmp_rel_mention_set

    def add_new_event_event_relation_mention_set(self):
        evt_evt_rel_men_set = self.construct_event_event_relation_mention_set()
        self.add_event_event_relation_mention_set(evt_evt_rel_men_set)
        return evt_evt_rel_men_set

    def construct_event_event_relation_mention_set(self):
        from serif.theory.event_event_relation_mention_set import EventEventRelationMentionSet
        event_event_rel_mention_set = EventEventRelationMentionSet.empty(owner=self)
        event_event_rel_mention_set.document.generate_id(
            event_event_rel_mention_set)
        return event_event_rel_mention_set

    def construct_rel_mention_set(self):
        from serif.theory.rel_mention_set import RelMentionSet
        rel_mention_set = RelMentionSet.empty(owner=self)
        rel_mention_set.document.generate_id(rel_mention_set)
        return rel_mention_set

    def add_new_rel_mention_set(self):
        rel_mention_set = self.construct_rel_mention_set()
        self.rel_mention_set = rel_mention_set
        return rel_mention_set

    def add_new_modal_temporal_relation_mention_set(self):
        mod_tmp_rel_men_set = self.construct_modal_temporal_relation_mention_set()
        self.add_modal_temporal_relation_mention_set(mod_tmp_rel_men_set)
        return mod_tmp_rel_men_set

    def construct_modal_temporal_relation_mention_set(self):
        from serif.theory.modal_temporal_relation_mention_set import ModalTemporalRelationMentionSet
        modal_temporal_rel_mention_set = ModalTemporalRelationMentionSet.empty(owner=self)
        modal_temporal_rel_mention_set.document.generate_id(
            modal_temporal_rel_mention_set)
        return modal_temporal_rel_mention_set

    def add_entity_set(self, entity_set):
        self.entity_set = entity_set

    def add_new_entity_set(self):
        entity_set = self.construct_entity_set()
        self.add_entity_set(entity_set)
        return entity_set

    def construct_entity_set(self):
        from serif.theory.entity_set import EntitySet
        entity_set = EntitySet.empty(owner=self)
        entity_set.document.generate_id(entity_set)
        return entity_set

    def add_value_set(self, value_set):
        self.value_set = value_set

    def add_new_value_set(self):
        value_set = self.construct_value_set()
        self.add_value_set(value_set)
        return value_set

    def construct_value_set(self):
        from serif.theory.value_set import ValueSet
        value_set = ValueSet.empty(owner=self)
        value_set.document.generate_id(value_set)
        return value_set

    def add_event_set(self, event_set):
        self.event_set = event_set

    def add_new_event_set(self):
        event_set = self.construct_event_set()
        self.add_event_set(event_set)
        return event_set

    def construct_event_set(self):
        from serif.theory.event_set import EventSet
        event_set = EventSet.empty(owner=self)
        event_set.document.generate_id(event_set)
        return event_set

    def add_relation_set(self, relation_set):
        self.relation_set = relation_set

    def add_new_relation_set(self):
        relation_set = self.construct_relation_set()
        self.add_relation_set(relation_set)
        return relation_set

    def construct_relation_set(self):
        relation_set = RelationSet.empty(owner=self)
        relation_set.document.generate_id(relation_set)
        return relation_set

    def add_new_actor_entity_set(self):
        actor_entity_set = self.construct_actor_entity_set()
        self.add_actor_entity_set(actor_entity_set)
        return actor_entity_set

    def construct_actor_entity_set(self):
        actor_entity_set = ActorEntitySet.empty(owner=self)
        actor_entity_set.document.generate_id(actor_entity_set)
        return actor_entity_set
        
    def add_actor_entity_set(self, actor_entity_set):
        self.actor_entity_set = actor_entity_set

    def add_new_sentences(self):
        sentences = self.construct_sentences()
        self.add_sentences(sentences)
        return sentences

    def construct_sentences(self):
        from serif.theory.sentences import Sentences
        sentences = Sentences.empty(owner=self)
        return sentences

    def add_sentences(self, sentences):
        self.sentences = sentences

    @staticmethod
    def construct(doc_id):
        document = Document(docid=doc_id)
        document.document.generate_id(document)
        return document

    @staticmethod
    def from_sgm(input_file, language):
        with open(input_file) as f:
            s = f.read()


            start_doc_tag = s.find("<DOC id=\"")
            start_docid_tag = s.find("<DOCID>")
            docid = ""
            if start_doc_tag != -1:
                start_id = start_doc_tag + 9
                end_id = s.find("\"", start_id + 1)
                docid = s[start_id:end_id].strip()
            elif start_docid_tag != -1:
                start_id = start_docid_tag + 7
                end_id = s.find("</", start_id + 1)
                docid = s[start_id:end_id].strip()

            contents_offset = (0, len(s) - 1)
            date_time_offset = (s.find("<DATETIME>") + 10, s.find("</DATETIME>") - 1)
            region_offset = (s.find("<TEXT>") + 6, s.find("</TEXT>") - 1)

            span_text_offset = (region_offset[0], region_offset[1] + 1)

            # TODO: do we need customized region detectors & segment detectors?
            logger.info("Creating a SERIF XML document")
            new_doc = Document.construct(docid)
            new_doc.language = language
            new_doc.construct_original_text(s, contents_offset[0], contents_offset[1])
            new_doc.construct_date_time(date_time_offset[0], date_time_offset[1])
            new_doc.construct_regions(region_offset[0], region_offset[1])
            new_doc.construct_segments()
            new_doc.construct_metadata(span_text_offset[0], span_text_offset[1], "RegionSpan", "TEXT")

            return new_doc

    @staticmethod
    def from_text(input_file, language, docid):
        with open(input_file, 'r', newline='', encoding='utf8') as f:
            s = f.read()
        return Document.from_string(s, language, docid)

    @staticmethod
    def from_string(s, language, docid):
        logger.info("Creating {} from text".format(docid))
        new_doc = Document.construct(docid)
        new_doc.language = language
        new_doc.construct_original_text(s, 0, max(len(s) - 1, 0))
        new_doc.construct_regions(0, max(len(s) - 1, 0))
        new_doc.construct_segments()
        new_doc.construct_metadata()
        return new_doc

