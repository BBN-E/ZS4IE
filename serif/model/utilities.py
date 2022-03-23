
def get_covering_node_rec(node, smallest_node, start, end, tok_seq, tags):

    s = tok_seq.index(node.start_token)
    e = tok_seq.index(node.end_token)

    if any(node.tag.startswith(t) for t in tags) and s <= start and e >= end:
        smallest_node = node

    # Prefer child NPs
    for child in node:
        smallest_node = get_covering_node_rec(
            child, smallest_node, start, end, tok_seq, tags)
      
    return smallest_node


def get_covering_np(sentence, name):
    return get_np_covering_tokens(sentence, name.start_token, name.end_token)


def get_np_covering_tokens(sentence, start_token, end_token):
    return get_covering_syn_node(
        sentence, start_token, end_token, ['NP'])


def get_covering_syn_node(sentence, start_token, end_token, tags):
    tok_seq = list(sentence.token_sequence)
    start = tok_seq.index(start_token)
    end = tok_seq.index(end_token)
    smallest_node = None
    root = sentence.parse.root
    smallest_node = get_covering_node_rec(
        root, smallest_node, start, end, tok_seq, tags)
    return smallest_node


