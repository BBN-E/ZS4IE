import serifxml3

def mark_sentence_with_mention(mention):
    tokens = list()
    for idx, token in enumerate(mention.sentence.token_sequence):
        c = ""
        if token is mention.start_token:
            c = c + "["
        c = c + token.text
        if token is mention.end_token:
            c = c + "]"
        tokens.append(c)
    return " ".join(tokens)

def print_ner(serif_doc):
    for sentence in serif_doc.sentences:
        for mention in sentence.mention_set or ():
            if mention.model == "Ask2Transformers":
                print("{}\t{}".format(mention.entity_type, mark_sentence_with_mention(mention)))

def mark_sentences_with_mention_pair(left_mention, right_mention):
    left_sent_no = left_mention.sentence.sent_no
    right_sent_no = right_mention.sentence.sent_no
    min_sent_no = min(left_sent_no, right_sent_no)
    max_sent_no = max(left_sent_no, right_sent_no)
    tokens = list()
    for sent_no in range(min_sent_no, max_sent_no + 1):
        serif_sent = left_mention.document.sentences[sent_no]
        for idx, token in enumerate(serif_sent.token_sequence):
            c = ""
            if token is left_mention.start_token:
                c = c + "["
            if token is right_mention.start_token:
                c = c + "<"
            c = c + token.text
            if token is right_mention.end_token:
                c = c + ">"
            if token is left_mention.end_token:
                c = c + "]"
            tokens.append(c)
    return " ".join(tokens)
def print_entity_mention_entity_mention_relation(serif_doc):
    for rel_mention in serif_doc.rel_mention_set or ():
        print("{}\t{}".format(rel_mention.type,mark_sentences_with_mention_pair(rel_mention.left_mention,rel_mention.right_mention)))

def main(serif_path_list):
    for serif_path in serif_path_list:
        serif_doc = serifxml3.Document(serif_path)
        print_ner(serif_doc)
        print_entity_mention_entity_mention_relation(serif_doc)



if __name__ == "__main__":
    serif_path_list = [
        "/home/hqiu/tmp/doc_1.xml"
    ]
    main(serif_path_list)