from serif.theory.actor_mention import ActorMention
from serif.theory.serif_sequence_theory import SerifSequenceTheory
from serif.xmlio import _ChildTheoryElementList


class ActorMentionSet(SerifSequenceTheory):
    _children = _ChildTheoryElementList('ActorMention')

    @classmethod
    def from_values(cls, owner=None):
        ret = cls(owner=owner)
        return ret

    @classmethod
    def empty(cls, owner=None):
        return cls.from_values(owner=owner)

    def add_new_actor_mention(self, mention, actor_db_name, actor_uid, actor_name, source_note):
        actor_mention = self.construct_actor_mention(mention, actor_db_name, actor_uid, actor_name, source_note)
        self.add_actor_mention(actor_mention)
        return actor_mention

    def construct_actor_mention(self, mention, actor_db_name, actor_uid, actor_name, source_note):
        actor_mention = ActorMention(owner=self)
        actor_mention.mention = mention
        actor_mention.actor_db_name = actor_db_name
        actor_mention.actor_uid = actor_uid
        actor_mention.actor_name = actor_name
        actor_mention.source_note = source_note
        actor_mention.document.generate_id(actor_mention)
        return actor_mention

    def add_actor_mention(self, actor_mention):
        self._children.append(actor_mention)
