from abc import abstractmethod

from serif.model.document_model import DocumentModel
from serif.model.validate import validate_sentence_tokens
from serif.theory.enumerated_type import Genericity, Polarity, Tense, Modality
from serifxml3 import Mention, ValueMention, EventMention, SynNode


class EventMentionModel(DocumentModel):

    def __init__(self, **kwargs):
        super(EventMentionModel, self).__init__(**kwargs)

    @abstractmethod
    def add_event_mentions_to_sentence(self, sentence):
        """
        :type sentence: Sentence
        :return: List where each element corresponds to one newly-added EventMention.
        :rtype: list(EventMention)
        """
        pass

    @staticmethod
    def add_new_event_mention(event_mention_set, event_type, start_token, end_token, *, score=0.0, pattern_id=None,
                              genericity=Genericity.Specific, polarity=Polarity.Positive,
                              direction_of_change=None, tense=Tense.Present, modality=Modality.Asserted,
                              state_of_affairs=None, anchor_prop=None, model=None,
                              genericityScore=None, modalityScore=None, cluster_id=None, completion=None,
                              coordinated=None, over_time=None, granular_template_type_attribute=None):
        """
        :type event_mention_set: EventMentionSet
        :type sentence: Sentence
        :type event_type: string
        :type start_token: Token
        :type end_token: Token
        :type score: float
        :type pattern_id:
        :type genericity: Genericity
        :type polarity: Polarity
        :type direction_of_change: DirectionOfChange
        :type tense: Tense
        :type modality: Modality
        :type state_of_affairs: bool
        :type anchor_prop: Proposition
        :type model: string
        :type genericityScore: float
        :type modalityScore: float
        :type cluster_id: int
        :type completion:
        :type coordinated: bool
        :type over_time: bool
        :type granular_template_type_attribute:
        :return: List where each element corresponds to one newly-added EventMention.
        :rtype: list(EventMention)
        """
        if start_token is None or end_token is None:
            return []
        # construct object
        sentence = event_mention_set.sentence
        anchor_node = EventMentionModel.identify_anchor_node(sentence, start_token,
                                                             end_token)  # anchor_node can be None but it's OK
        event_mention = event_mention_set.add_new_event_mention(event_type, anchor_node, score)
        event_mention.semantic_phrase_start = start_token.index()
        event_mention.semantic_phrase_end = end_token.index()
        event_mention.pattern_id = pattern_id
        event_mention.genericity = genericity
        event_mention.polarity = polarity
        event_mention.direction_of_change = direction_of_change
        event_mention.tense = tense
        event_mention.modality = modality
        event_mention.state_of_affairs = state_of_affairs
        event_mention.anchor_prop = anchor_prop
        event_mention.model = model
        event_mention.genericityScore = genericityScore
        event_mention.modalityScore = modalityScore
        event_mention.cluster_id = cluster_id
        event_mention.completion = completion
        event_mention.coordinated = coordinated
        event_mention.over_time = over_time
        event_mention.granular_template_type_attribute = granular_template_type_attribute
        return [event_mention]

    @staticmethod
    def identify_anchor_node(sentence, start_token, end_token):
        """
        :type sentence: Sentence
        :type start_token: Token
        :type end_token: Token
        :return: SynNode that spans start_token to end_token exactly
        :rtype: SynNode
        """
        if sentence.parse is not None:
            node = sentence.parse.get_covering_syn_node(start_token, end_token, [])
            if node.start_token == start_token and node.end_token == end_token:
                return node
        return None

    @staticmethod
    def add_new_event_mention_argument(event_mention, role, mention, arg_score, *, model=None, pattern=None):
        """
        :type event_mention: EventMention
        :type role: string
        :type mention: Mention, ValueMention, EventMention or SynNode
        :type arg_score: float
        :return: List where each element corresponds to one newly-added argument.
        :rtype: list(EventMentionArg)
        """
        new_args = []
        arg = None
        if isinstance(mention, Mention):
            arg = event_mention.add_new_mention_argument(role, mention, arg_score)
        elif isinstance(mention, ValueMention):
            arg = event_mention.add_new_value_mention_argument(role, mention, arg_score)
        elif isinstance(mention, EventMention):
            arg = event_mention.add_new_event_mention_argument(role, mention, arg_score)
        elif isinstance(mention, SynNode):
            arg = event_mention.add_new_syn_node_argument(role, mention, arg_score)
        else:
            raise RuntimeError("Unexpected mention {} of type {}".format(
                mention,
                type(mention)))
            # raise RuntimeError("Bad argument role {} in EventMention".format(role))
        if arg is not None:
            new_args.append(arg)
            arg.model = model
            arg.pattern = pattern
        return new_args

    def process_document(self, serif_doc):
        for i, sentence in enumerate(serif_doc.sentences):
            validate_sentence_tokens(sentence, serif_doc.docid, i)
            event_mention_set = sentence.event_mention_set
            if event_mention_set is None:
                event_mention_set = \
                    sentence.add_new_event_mention_set()
                ''':type: EventMentionSet'''
            self.add_event_mentions_to_sentence(sentence)
