from serif.theory.enumerated_type import MentionType
from serif.theory.mention import Mention
from serif.theory.parse import Parse
from serif.theory.serif_sequence_theory import SerifSequenceTheory
from serif.xmlio import _SimpleAttribute, _ReferenceAttribute, _ChildTheoryElementList


class MentionSet(SerifSequenceTheory):
    name_score = _SimpleAttribute(float)
    desc_score = _SimpleAttribute(float)
    parse = _ReferenceAttribute('parse_id', cls=Parse)
    _children = _ChildTheoryElementList('Mention')

    @classmethod
    def from_values(cls, owner=None, parse=None, name_score=0, desc_score=0):
        ret = cls(owner=owner)
        ret.parse = parse
        ret.name_score = name_score
        ret.desc_score = desc_score
        return ret

    @classmethod
    def empty(cls, owner=None, parse=None):
        return cls.from_values(owner=owner, parse=parse)

    def add_mention(self, mention):
        self._children.append(mention)

    def add_new_mention(self, syn_node, mention_type, entity_type):
        mention = self.construct_mention(syn_node, mention_type, entity_type, syn_node.tokens[0], syn_node.tokens[-1])
        self.add_mention(mention)
        return mention

    def add_new_mention_from_tokens(self, mention_type, entity_type, start_token, end_token):
        mention = self.construct_mention(None, mention_type, entity_type, start_token, end_token)
        self.add_mention(mention)
        return mention

    def construct_mention(self, syn_node, mention_type, entity_type, start_token, end_token):
        mention = Mention(owner=self)
        mention.syn_node = syn_node
        mention.entity_type = entity_type
        mention.start_token = start_token
        mention.end_token = end_token
        umt = mention_type.upper()
        if umt == "NONE":
            mention.mention_type = MentionType.none
        elif umt == "NAME":
            mention.mention_type = MentionType.name
        elif umt == "PRON":
            mention.mention_type = MentionType.pron
        elif umt == "DESC":
            mention.mention_type = MentionType.desc
        elif umt == "PART":
            mention.mention_type = MentionType.part
        elif umt == "APPO":
            mention.mention_type = MentionType.appo
        elif umt == "LIST":
            mention.mention_type = MentionType.list
        elif umt == "NEST":
            mention.mention_type = MentionType.nest
        else:
            mention.mention_type = MentionType.none
        mention.document.generate_id(mention)
        return mention
