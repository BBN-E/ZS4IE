# Used by DependencySet, stores dependency information in a structured way

class AugmentedArgument:
    
    def __init__(self, role, syn_node, mention, value_mention, event_mention):
        self.role = role
        self.syn_node = syn_node
        self.mention = mention
        self.value_mention = value_mention
        self.event_mention = event_mention

    def get_summary(self):
        s = self.role + ":\n"
        if self.syn_node:
            s += "  SynNode: " + str(self.syn_node) + "\n"
        if self.mention:
            s += "  Mention: " + self.mention.text + "\n"
        if self.value_mention:
            s += "  ValueMention: " + self.value_mention.text + "\n"
        if self.event_mention:
            s += "  EventMention: " + str(self.event_mention.anchor_node) + "\n"
        return s
