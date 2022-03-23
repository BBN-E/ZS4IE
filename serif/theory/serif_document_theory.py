import re
import weakref

from serif.theory.serif_theory import SerifTheory
from serif.xmlio import ET, SERIFXML_VERSION


class SerifDocumentTheory(SerifTheory):
    def __init__(self, etree=None, owner=None, **attribs):
        self._idmap = weakref.WeakValueDictionary()
        self._id_re = re.compile(r'a(\d+)$')
        self._highest_id = -1
        SerifTheory.__init__(self, etree, owner, **attribs)

    _OWNER_IS_REQUIRED = False

    def _init_from_etree(self, etree, owner):
        # If the argument isn't an etree, then create one.
        if hasattr(etree, 'makeelement'):
            pass  # ok.
        elif hasattr(etree, 'getroot'):
            etree = etree.getroot()  # ElementTree object
        elif isinstance(etree, str):
            if re.match('^\s*<', etree):
                etree = ET.fromstring(etree)  # xml string
            elif '\n' not in etree:
                etree = ET.parse(etree).getroot()  # filename
            else:
                raise ValueError('Expected a filename, xml string, stream, '
                                 'or ElementTree.  Got a %s' %
                                 etree.__class__.__name__)
        elif hasattr(etree, 'read'):
            etree = ET.fromstring(etree.read())  # file object
        else:
            raise ValueError('Expected a filename, xml string, stream, '
                             'or ElementTree.  Got a %s' %
                             etree.__class__.__name__)
        # If we got a SerifXML element, then take its document.
        if (etree.tag == 'SerifXML' and len(etree) == 1 and
                etree[0].tag == 'Document'):
            etree = etree[0]
        SerifTheory._init_from_etree(self, etree, owner)
        # Resolve pointers.
        self.resolve_pointers()

    def save(self, file_or_filename):
        serifxml_etree = ET.Element('SerifXML')
        serifxml_etree.text = '\n  '
        serifxml_etree.attrib['version'] = str(SERIFXML_VERSION)
        etree = getattr(self, '_etree', None)
        serifxml_etree.append(self.toxml(etree, indent='  '))
        ET.ElementTree(serifxml_etree).write(file_or_filename, encoding='utf-8')

    def register_id(self, theory):
        if theory.id is not None:
            if theory.id in self._idmap:
                raise ValueError('Duplicate id %s' % theory.id)
            self._idmap[theory.id] = theory
            m = self._id_re.match(theory.id)
            if m:
                current_id_int = int(m.group(1))
                if current_id_int > self._highest_id:
                    self._highest_id = current_id_int

    def lookup_id(self, theory_id):
        return self._idmap.get(theory_id)

    def generate_id(self, theory):
        self._highest_id += 1
        theory.id = "a" + str(self._highest_id)
        self.register_id(theory)

    _default_hidden_attrs = {'lexicon'}

    def entity_by_mention(self, mention):
        """Returns the Entity which contains the given Mention"""
        if self.entity_set is None:
            return None
        for entity in self.entity_set:
            for m in entity.mentions:
                if mention == m:
                    return entity
        return None
    
    def entity_by_mention_no_type_check(self, mention):
        """Returns the Entity which contains the given Mention"""
        if self.entity_set is None:
            return None
        for entity in self.entity_set:
            for m in entity.mentions:
                if mention == m:
                    return entity
        return None

    def entity_by_mention_with_type_check(self, mention):
        """Returns the Entity which contains the given Mention
           but only when entity type matches"""
        if self.entity_set is None:
            return None
        for entity in self.entity_set:
            if entity.entity_type == mention.entity_type:
                for m in entity.mentions:
                    if mention == m:
                        return entity
        return None

    def get_entity_to_actor_entity_cache(self):
        """Returns a dict containing high confidence entity -> actor
           links. The dict has a key of Entity and an value of 
           ActorEntity. The value 0.55 is used as a threshold for
           high confidence because CSerif should return at most one
           actor link with higher than 0.55 confidence.
        """
        entity_to_actor_entity = dict()
        for ae in self.actor_entity_set:
            if ae.confidence < 0.55 or ae.actor_uid is None:
                continue
            entity_to_actor_entity[ae.entity] = ae
        return entity_to_actor_entity

