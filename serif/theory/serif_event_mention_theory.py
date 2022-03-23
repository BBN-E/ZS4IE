from serif.theory.serif_theory import SerifTheory

class SerifEventMentionTheory(SerifTheory):
    
    def mention_arguments(self):
        """Returns a list of just the Mention arguments in this EventMention"""
        results = []
        for arg in self.arguments:
            if arg.mention != None:
                results.append(arg)
        return results

    def value_mention_arguments(self):
        """Returns a list of just the ValueMention arguments in
           this EventMention
        """
        results = []
        for arg in self.arguments:
            if arg.value_mention != None:
                results.append(arg)
        return results
