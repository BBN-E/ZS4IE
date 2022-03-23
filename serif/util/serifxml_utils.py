import os

class CountryIdentifier:
    initialized = False
    lowercase_country_strings = set()
    
    @classmethod 
    def load_countries_list(cls):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        countries_list = os.path.realpath(os.path.join(
            script_dir, os.pardir, os.pardir, os.pardir, "java", "serif", "src", "main",
            "resources", "com", "bbn", "serif", "coreference", 
            "representativementions", "nationality-canonical-names"))
        with open(countries_list) as c:
            for line in c:
                line = line.strip()
                if len(line) == 0 or line.startswith("#"):
                    continue
                pieces = line.split(":", 1)
                CountryIdentifier.lowercase_country_strings.add(pieces[1].lower())
                CountryIdentifier.initialized = True

    @classmethod 
    def is_country_string(cls, s):
        if not CountryIdentifier.initialized:
            CountryIdentifier.load_countries_list()
        return s.lower() in CountryIdentifier.lowercase_country_strings


def exist_in_event_mention_set(event_mention_set, event_type, event_anchor_synnode, event_start_token_index, event_end_token_index, trigger_start_char, trigger_end_char, trigger_text=None):
    for event_mention in event_mention_set:
        if event_mention.event_type != event_type:
            continue

        if event_mention.anchor_node and event_mention.anchor_node.start_char == trigger_start_char and event_mention.anchor_node.end_char == trigger_end_char:
            return event_mention
        if event_mention.anchor_node and event_anchor_synnode and event_mention.anchor_node.start_char == event_anchor_synnode.start_char and event_mention.anchor_node.end_char == event_anchor_synnode.end_char:
            return event_mention
        if event_mention.semantic_phrase_start == event_start_token_index and event_mention.semantic_phrase_end == event_end_token_index:
            return event_mention


        for anchor in event_mention.anchors or []:
            if anchor.anchor_node:
                if anchor.anchor_node.start_char == trigger_start_char and anchor.anchor_node.end_char == trigger_end_char:
                    return event_mention
                if event_anchor_synnode and anchor.anchor_node.start_char == event_anchor_synnode.start_char and anchor.anchor_node.end_char == event_anchor_synnode.end_char:
                    return event_mention

    return None

