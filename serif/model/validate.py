
def validate_doc_sentences(doc):
    if doc.sentences is None:
        raise IOError(
            'WARNING: Document {} has no Sentences container'.format(doc.docid))

def validate_doc_entity_sets(doc):
    if doc.entity_set is None:
        raise IOError(
            'WARNING: Document {} has no Entities container'.format(doc.docid))
def validate_sentence_tokens(sentence, docid, sentence_count):
    if sentence.token_sequence is None:
        raise IOError(
            'WARNING: Sentence #{} ({}) in Document {} has no TokenSequence '
            'container'.format(sentence_count, sentence.id, docid))
    elif any(t.text is None for t in sentence.token_sequence):
        j = None
        t_id = None
        for j, token in enumerate(sentence.token_sequence):
            t_id = token.id
            if token.text is None:
                break
        raise IOError(
            'WARNING: Token #{} ({}) in Sentence #{} ({}) in Document {} has '
            'no `text` attribute'
            .format(j, t_id, sentence_count, sentence.id, docid))

def validate_sentence_value_mention_set(sentence, docid, sentence_count):
    if sentence.value_mention_set is None:
        raise IOError(
            'WARNING: Sentence #{} ({}) in Document {} has no ValueMentionSet '
            'container'.format(sentence_count, sentence.id, docid))

def validate_sentence_parse(sentence, docid, sentence_count):

    def _delve(node):
        # TODO should include other attributes?
        if node.start_token is None:
            raise IOError(
                "WARNING: Sentence #{} ({}) in Document {} has Parse containing"
                " a SynNode ({}) with no start Token"
                .format(sentence_count, sentence.id, docid, node.id))
        if node.end_token is None:
            raise IOError(
                "WARNING: Sentence #{} ({}) in Document {} has Parse containing"
                " a SynNode ({}) with no end Token"
                .format(sentence_count, sentence.id, docid, node.id))
        if node.tag is None:
            raise IOError(
                "WARNING: Sentence #{} ({}) in Document {} has Parse containing"
                " a SynNode ({}) with no `tag` string"
                .format(sentence_count, sentence.id, docid, node.id))
        for child in node:
            _delve(child)

    if sentence.parse is None:
        raise IOError("WARNING: Sentence #{} ({}) in Document {} has no Parse"
                      .format(sentence_count, sentence.id, docid))
    elif sentence.parse.root is None:
        raise IOError(
            "WARNING: Sentence #{} ({}) in Document {} has a Parse with no root"
            " SynNode".format(sentence_count, sentence.id, docid))
    _delve(sentence.parse.root)

def validate_sentence_mention_sets(sentence, docid, sentence_count):
    if sentence.mention_set is None:
        raise IOError("WARNING: Sentence #{} ({}) in Document {} has no MentionSet"
                      .format(sentence_count, sentence.id, docid))

def validate_sentence_relation_mention_sets(sentence, docid, sentence_count):
    if sentence.rel_mention_set is None:
        raise IOError(
            "WARNING: Sentence #{} ({}) in Document {} has no RelMentionSet"
            .format(sentence_count, sentence.id, docid))

def validate_sentence_event_mention_sets(sentence, docid, sentence_count):
    if sentence.event_mention_set is None:
        raise IOError(
            "WARNING: Sentence #{} ({}) in Document {} has no EventMentionSet"
            .format(sentence_count, sentence.id, docid))
