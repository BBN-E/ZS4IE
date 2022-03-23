import sys, os

from serif.theory.serif_theory import SerifTheory
from serif.theory.enumerated_type import MentionType

from serif.util.serifxml_utils import CountryIdentifier

class SerifEntityTheory(SerifTheory):

    def num_mentions(self):
        """Returns the number or mentions in this Entity"""
        return len(self.mentions)

    def representative_mention(self):
        """Finds the mentions that best represents the Entity. Algorithm
           ported from Java's DefaultRepresentativeMentionFinder."""
        
        # Look for country name first but calculate longest name as well
        longest_name_mention = None
        longest_length = None
        for mention in self.mentions:
            if mention.mention_type != MentionType.name:
                continue
            
            name = mention.text
            if mention.atomic_head is not None:
                name = mention.atomic_head.text.lower()
            if longest_name_mention is None or len(name) > longest_length:
                longest_name_mention = mention
                longest_length = len(name)
            if CountryIdentifier.is_country_string(name):
                return mention
        
        # Longest name
        if longest_name_mention: 
            return longest_name_mention
        
        # Earliest desc (or longest if tie)
        earliest_desc_mention = None
        earliest_char_offset = None
        earliest_desc_mention_length = None
        for mention in self.mentions:
            if mention.mention_type != MentionType.desc:
                continue
            if (earliest_desc_mention is None or 
                mention.start_char < earliest_char_offset or
                (mention.start_char == earliest_char_offset and
                 len(mention.text) > earliest_desc_mention_length)):
                earliest_desc_mention = mention
                earliest_char_offset = mention.start_char
                earliest_desc_mention_length = len(mention.text)
        if earliest_desc_mention:
            return earliest_desc_mention
        
        # Default, could happen with first person pronouns?
        if len(self.mentions) > 0:
            return self.mentions[0]
        
        return None

    def representative_name(self):
        """Finds the most 'representative name' from the list of Mentions. 
           If there is no name Mention in the Entity, this will return None. 
           Algorithm is ported from Java."""
        rm = self.representative_mention()
        if rm is not None and rm.mention_type == MentionType.name:
            return rm
        return None

    def contains_mention(self, mention):
        """Returns true if given Mention is part of the Entity"""
        for m in self.mentions:
            if m == mention: 
                return True
        return False

    def has_name_mention(self):
        """Returns true if there is a name Mention in the Entity"""
        for m in self.mentions:
            if m.mention_type == MentionType.name:
                return True
        return False

    def has_desc_mention(self):
        """Returns true if there is a desc Mention in the Entity"""
        for m in self.mentions:
            if m.mention_type == MentionType.desc:
                return True
        return False

    def has_name_or_desc_mention(self):
        """Returns true if there is a name or desc Mention in the Entity"""
        for m in self.mentions:
            if (m.mention_type == MentionType.desc or 
                m.mention_type == MentionType.name):
              return True
        return False
