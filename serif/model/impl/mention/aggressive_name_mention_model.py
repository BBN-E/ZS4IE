from serif.model.document_model import DocumentModel
from serif.theory.enumerated_type import MentionType

import logging

# Unlike NameMentionModel, this won't throw out any names when it
# can't find an NP node that exactly matches the name extent. 
# It will create name mentions from just start and end token if 
# it can't find a matching syn node. We tried matching any node
# not just NP, but that screws up the mention.atomic_head
# function.

# The reason why we inherit from BaseModel and not MentionModel
# is because MentionModel only makes mentions out of syn nodes, 
# and we want to be able to make mentions out of start and
# end tokens.

logger = logging.getLogger(__name__)

class AggressiveNameMentionModel(DocumentModel):
    """Makes Mentions for existing Names, doesn't throw out any names"""

    def __init__(self,**kwargs):
        super(AggressiveNameMentionModel,self).__init__(**kwargs)

    def name_mention_from_syn_node(self, sentence, entity_type, syn_node):
        # check for existing mention with syn_node
        found = False
        for mention in sentence.mention_set:
            if mention.syn_node == syn_node or mention.atomic_head == syn_node:
                found = True
                mention.mention_type = MentionType.name
                mention.entity_type = entity_type
        if found: return

        # create new
        sentence.mention_set.add_new_mention(syn_node, "NAME", entity_type)

    def name_mention_from_tokens(self, sentence, entity_type, start_token, end_token):
        # check for existing mention with syn_node
        found = False
        for mention in sentence.mention_set:
            if mention.start_token == start_token and mention.end_token == end_token:
                found = True
                mention.mention_type = MentionType.name
                mention.entity_type = entity_type
        if found: return
        
        # create new
        sentence.mention_set.add_new_mention_from_tokens("NAME", entity_type, start_token, end_token)
        
    def process_document(self, document):
        for sentence in document.sentences:

            if sentence.mention_set is None:
                sentence.add_new_mention_set()

            if sentence.name_theory is None:
                logger.warning("No name theory for sentence {}, skipping AggressiveNameMentionModel".
                               format(sentence.id))
                continue
            elif sentence.parse is None:
                logger.warning("No parse for sentence {}, skipping AggressiveNameMentionModel".
                               format(sentence.id))
                continue

            for name in sentence.name_theory:
                
                # Exact match NP
                syn_node = sentence.parse.get_covering_syn_node(
                    name.start_token, name.end_token, ["NP"])
                
                if (syn_node and 
                        syn_node.start_token == name.start_token and
                        syn_node.end_token == name.end_token):
                    self.name_mention_from_syn_node(sentence, name.entity_type, syn_node)
                    continue

                # Just create mention from start and end token
                self.name_mention_from_tokens(sentence, name.entity_type, name.start_token, name.end_token)
