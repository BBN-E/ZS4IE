from serif.theory.augmented_argument import AugmentedArgument
from serif.theory.enumerated_type import MentionType
from serif.theory.enumerated_type import PredType
from serif.theory.mention_set import MentionSet
from serif.theory.proposition import Proposition
from serif.theory.serif_sequence_theory import SerifSequenceTheory
from serif.xmlio import _ReferenceAttribute, _ChildTheoryElementList


class DependencySet(SerifSequenceTheory):
    mention_set = _ReferenceAttribute('mention_set_id', cls=MentionSet)
    _children = _ChildTheoryElementList('Proposition')

    @classmethod
    def from_values(cls, owner=None, mention_set=None):
        ret = cls(owner=owner)
        ret.mention_set = mention_set
        return ret

    @classmethod
    def empty(cls, owner=None, mention_set=None):
        return cls.from_values(owner=owner, mention_set=mention_set)

    def add_proposition(self, proposition):
        self._children.append(proposition)

    def add_new_proposition(self, pred_type, head_node):
        proposition = self.construct_proposition(pred_type, head_node)
        self.add_proposition(proposition)
        return proposition

    def construct_proposition(self, pred_type, head_node):
        proposition = Proposition(owner=self)
        proposition.head = head_node
        upt = pred_type.upper()
        if upt == "VERB":
            proposition.pred_type = PredType.verb
        elif upt == "COPULA":
            proposition.pred_type = PredType.copula
        elif upt == "MODIFIER":
            proposition.pred_type = PredType.modifier
        elif upt == "NOUN":
            proposition.pred_type = PredType.noun
        elif upt == "POSS":
            proposition.pred_type = PredType.poss
        elif upt == "LOC":
            proposition.pred_type = PredType.loc
        elif upt == "SET":
            proposition.pred_type = PredType.set
        elif upt == "NAME":
            proposition.pred_type = PredType.name
        elif upt == "PRONOUN":
            proposition.pred_type = PredType.pronoun
        elif upt == "COMP":
            proposition.pred_type = PredType.comp
        elif upt == "DEPENDENCY":
            proposition.pred_type = PredType.dependency
        else:
            raise Exception("Unknown pred_type: " + pred_type)
        proposition.document.generate_id(proposition)
        return proposition

    def get_root_proposition(self):
        props_that_are_arguments = set()
        for proposition in self:
            for arg in proposition.arguments:
                props_that_are_arguments.add(arg.proposition)
        for proposition in self:
            if proposition not in props_that_are_arguments:
                return proposition
        return None

    def find_matching_syn_node(self, proposition, value_mention):
        head = proposition.head
        if (head.start_char >= value_mention.start_char and
                head.end_char <= value_mention.end_char):
            return proposition.head
        for arg in proposition.arguments:
            if arg.proposition is not None:
                match = self.find_matching_syn_node(arg.proposition, value_mention)
                if match is not None:
                    return match
            if arg.syn_node is not None:
                syn_node = arg.syn_node
                if (syn_node.start_char >= value_mention.start_char and
                        syn_node.end_char <= value_mention.end_char):
                    return syn_node
        return None

    # Produces a list containing the dependency info connected to 
    # mentions, value mentions and event mentions
    def get_dependency_info(self, mention_set, value_mention_set, event_mention_set):
        results = []
        syn_node_to_mention = dict()
        for mention in mention_set or []:
            if mention.mention_type == MentionType.none:
                continue
            if mention.syn_node is not None:
                syn_node_to_mention[mention.syn_node.head] = mention

        syn_node_to_event_mention = dict()
        for event_mention in event_mention_set or []:
            if event_mention.anchor_node is not None:
                anchor = event_mention.anchor_node
                if anchor.is_terminal:
                    anchor = anchor.parent
                else:
                    anchor = anchor.head_preterminal
                syn_node_to_event_mention[anchor] = event_mention

        syn_node_to_value_mention = dict()
        for value_mention in value_mention_set or []:
            syn_node = self.find_matching_syn_node(self.get_root_proposition(), value_mention)
            syn_node_to_value_mention[syn_node] = value_mention

        for proposition in self:
            if len(proposition.arguments) == 0:
                continue
            augmented_args = []
            for arg in proposition.arguments:
                head = None
                if arg.proposition is not None:
                    head = arg.proposition.head
                elif arg.syn_node is not None:
                    head = arg.syn_node
                else:
                    continue

                mention = None
                value_mention = None
                event_mention = None

                if head in syn_node_to_mention:
                    mention = syn_node_to_mention[head]
                if head in syn_node_to_event_mention:
                    event_mention = syn_node_to_event_mention[head]
                if head in syn_node_to_value_mention:
                    value_mention = syn_node_to_value_mention[head]
                augmented_args.append(AugmentedArgument(arg.role, head, mention, value_mention, event_mention))

            results.append((proposition.head, augmented_args))

        return results
