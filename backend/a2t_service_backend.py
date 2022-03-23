import datetime
import io
import json
import os
import sys
import time

import yaml

current_script_path = __file__
project_root = os.path.realpath(
    os.path.join(current_script_path, os.path.pardir, os.path.pardir))
sys.path.append(project_root)

import flask
import flask_cors
import logging

logger = logging.getLogger(__name__)
from serif.theory.document import Document
from serif.driver.pipeline_service_base import PySerifPipeline, DuckClass, assemble_pipeline
from serif.model.impl.a2t_adapter.A2TDriver import A2TDriver
from serif.model.impl.a2t_adapter.special_text_parser import convert_marked_text_into_plain_text_and_markings, \
    add_spans_into_serifxml
from serif.model.impl.a2t_adapter.utils import modify_serifxml_from_unary_markings


def serifxml_to_string(serif_doc):
    with io.BytesIO() as byte_io:
        serif_doc.save(byte_io)
        byte_io.seek(0)
        return byte_io.read().decode("utf-8")


def generate_mention_key(doc_id, sent_idx, mention_entry):
    return (
        doc_id, sent_idx, mention_entry["start_token_idx"], mention_entry["end_token_idx"],
        mention_entry["entity_type"])


def generate_entity_relation_key(doc_id, left_mention_key, right_mention_key, relation_entry):
    return (doc_id, left_mention_key, right_mention_key, relation_entry["rel_type"])


def generate_event_mention_key(doc_id, sent_idx, event_mention_entry):
    return (doc_id, sent_idx, event_mention_entry["start_token_idx"],
            event_mention_entry["end_token_idx"], event_mention_entry["event_type"])


def generate_event_argument_key(doc_id, event_mention_key, mention_key, event_arg_entry):
    return (doc_id, event_mention_key, mention_key, event_arg_entry["role"])


def serif_json_seralizer(serif_doc):
    ret = dict()
    ret["doc_id"] = serif_doc.docid
    ret["sentences"] = list()
    ret["entity_relations"] = list()
    ret["mention_id_to_mention_loc"] = dict()
    ret["event_mention_id_to_event_mention_loc"] = dict()
    timestamp = int(time.time())
    for sent_no, sentence in enumerate(serif_doc.sentences or ()):
        sent_dict = dict()
        ret["sentences"].append(sent_dict)
        sent_dict["unary_markings"] = {
            "mentions": [],
            "event_mentions": []
        }
        sent_dict["sent_no"] = sent_no
        sent_dict["tokens"] = list()
        for token_idx, token in enumerate(sentence.token_sequence):
            sent_dict["tokens"].append(
                {
                    "sent_no": sent_no,
                    "token_idx": token_idx,
                    "text": token.text
                }
            )
        sent_dict["mentions"] = list()
        for mention in sentence.mention_set or ():
            start_token_idx = mention.start_token.index()
            end_token_idx = mention.end_token.index()
            mention_id = "{}#{}#{}#{}".format(serif_doc.docid, type(mention).__name__, mention.id, timestamp)
            sent_dict["mentions"].append({
                "mention_id": mention_id,
                "start_token_idx": start_token_idx,
                "end_token_idx": end_token_idx,
                "mention_type": mention.mention_type.value,
                "entity_type": mention.entity_type,
                "model": mention.model,
                "pattern": mention.pattern,
                "confidence": mention.confidence,
                "is_frozen": False,
                "is_good": True,
            })
            ret["mention_id_to_mention_loc"][mention_id] = (sent_no, len(sent_dict["mentions"]) - 1)
        sent_dict["event_mentions"] = list()
        for event_mention in sentence.event_mention_set or ():
            start_token_idx = event_mention.semantic_phrase_start
            end_token_idx = event_mention.semantic_phrase_end
            event_args = list()
            for event_arg in event_mention.arguments:
                role = event_arg.role
                ref = event_arg.value
                event_args.append({
                    "role": role,
                    "ref": "{}#{}#{}#{}".format(serif_doc.docid, type(ref).__name__, ref.id, timestamp),
                    "model": event_arg.model,
                    "pattern": event_arg.pattern,
                    "is_frozen": False,
                    "is_good": True,
                })
            event_mention_id = "{}#{}#{}#{}".format(serif_doc.docid, type(event_mention).__name__, event_mention.id,
                                                    timestamp)
            sent_dict["event_mentions"].append({
                "event_mention_id": event_mention_id,
                "start_token_idx": start_token_idx,
                "end_token_idx": end_token_idx,
                "event_type": event_mention.event_type,
                "event_args": event_args,
                "model": event_mention.model,
                "score": event_mention.score,
                "pattern_id": event_mention.pattern_id,
                "is_frozen": False,
                "is_good": True,
            })
            ret["event_mention_id_to_event_mention_loc"][event_mention_id] = (
                sent_no, len(sent_dict["event_mentions"]) - 1)
    for rel_mention in serif_doc.rel_mention_set or ():
        rel_id = "{}#{}#{}#{}".format(serif_doc.docid, type(rel_mention).__name__, rel_mention.id, timestamp)
        left_mention = rel_mention.left_mention
        right_mention = rel_mention.right_mention
        rel_type = rel_mention.type
        pattern = rel_mention.pattern
        score = rel_mention.score
        ret["entity_relations"].append({
            "left_mention_id": "{}#{}#{}#{}".format(serif_doc.docid, type(left_mention).__name__, left_mention.id,
                                                    timestamp),
            "right_mention_id": "{}#{}#{}#{}".format(serif_doc.docid, type(right_mention).__name__, right_mention.id,
                                                     timestamp),
            "rel_mention_id": rel_id,
            "rel_type": rel_type,
            "pattern": pattern,
            "score": score,
            "model": rel_mention.model,
            "is_frozen": False,
            "is_good": True,
        })
    ret["annotation"] = dict()
    return ret


def build_json_id_to_json_entries(json_doc):
    mention_id_to_mention = dict()
    mention_id_to_sentence = dict()
    event_mention_id_to_event_mention = dict()
    event_mention_id_to_sentence = dict()
    for sentence in json_doc["sentences"]:
        for mention in sentence["mentions"]:
            mention_id_to_mention[mention["mention_id"]] = mention
            mention_id_to_sentence[mention["mention_id"]] = sentence
        for event_mention in sentence["event_mentions"]:
            event_mention_id_to_event_mention[event_mention["event_mention_id"]] = event_mention
            event_mention_id_to_sentence[event_mention["event_mention_id"]] = sentence
    return mention_id_to_mention, mention_id_to_sentence, event_mention_id_to_event_mention, event_mention_id_to_sentence


def build_customer_k_to_objects(json_doc, mention_id_to_mention, mention_id_to_sentence,
                                event_mention_id_to_event_mention, event_mention_id_to_sentence):
    mention_k_to_mentions_annos_j = dict()
    entity_relation_k_to_entity_relations_annos_j = dict()
    event_mention_k_to_event_mentions_annos_j = dict()
    event_arg_k_to_event_args_annos_j = dict()
    for sentence in json_doc["sentences"]:
        for mention in sentence["mentions"]:
            mention_key = generate_mention_key(json_doc["doc_id"], sentence["sent_no"], mention)
            mention_k_to_mentions_annos_j.setdefault(mention_key, list()).append(mention)
    for sentence in json_doc["sentences"]:
        for event_mention in sentence["event_mentions"]:
            event_mention_key = generate_event_mention_key(json_doc["doc_id"], sentence["sent_no"], event_mention)
            event_mention_k_to_event_mentions_annos_j.setdefault(event_mention_key, list()).append(event_mention)
            for event_arg in event_mention["event_args"]:
                right_mention = mention_id_to_mention[event_arg["ref"]]
                right_sentence = mention_id_to_sentence[event_arg["ref"]]
                right_mention_key = generate_mention_key(json_doc["doc_id"], right_sentence["sent_no"], right_mention)
                event_arg_key = generate_event_argument_key(json_doc["doc_id"], event_mention_key, right_mention_key,
                                                            event_arg)
                event_arg_k_to_event_args_annos_j.setdefault(event_arg_key, list()).append(event_arg)
    for entity_relation in json_doc["entity_relations"]:
        left_mention = mention_id_to_mention[entity_relation["left_mention_id"]]
        left_sentence = mention_id_to_sentence[entity_relation["left_mention_id"]]
        right_mention = mention_id_to_mention[entity_relation["right_mention_id"]]
        right_sentence = mention_id_to_sentence[entity_relation["right_mention_id"]]
        left_mention_key = generate_mention_key(json_doc["doc_id"], left_sentence["sent_no"], left_mention)
        right_mention_key = generate_mention_key(json_doc["doc_id"], right_sentence["sent_no"], right_mention)
        entity_relation_key = generate_entity_relation_key(json_doc["doc_id"], left_mention_key, right_mention_key,
                                                           entity_relation)
        entity_relation_k_to_entity_relations_annos_j.setdefault(entity_relation_key, list()).append(entity_relation)
    return mention_k_to_mentions_annos_j, entity_relation_k_to_entity_relations_annos_j, event_mention_k_to_event_mentions_annos_j, event_arg_k_to_event_args_annos_j


def resolve_annotation(annotation_json_doc, extraction_json_doc):
    extraction_json_doc["annotation"] = annotation_json_doc["annotation"]
    # Use UI data for overriding annotation
    mention_id_to_mention_anno, mention_id_to_sentence_anno, event_mention_id_to_event_mention_anno, event_mention_id_to_sentence_anno = build_json_id_to_json_entries(
        annotation_json_doc)
    mention_k_to_mentions_annos_j, entity_relation_k_to_entity_relations_annos_j, event_mention_k_to_event_mentions_annos_j, event_arg_k_to_event_args_annos_j = build_customer_k_to_objects(
        annotation_json_doc, mention_id_to_mention_anno, mention_id_to_sentence_anno,
        event_mention_id_to_event_mention_anno, event_mention_id_to_sentence_anno)
    for mention_k, mentions in mention_k_to_mentions_annos_j.items():
        for mention in mentions:
            if mention["is_frozen"]:
                string_mention_k = "{}#{}".format("Mention", "#".join(str(i) for i in mention_k))
                extraction_json_doc["annotation"][string_mention_k] = mention["is_good"]
    for entity_relation_k, entity_relations in entity_relation_k_to_entity_relations_annos_j.items():
        for entity_relation in entity_relations:
            if entity_relation["is_frozen"]:
                string_entity_relation_k = "{}#{}".format("EntityRelation", "#".join(str(i) for i in entity_relation_k))
                extraction_json_doc["annotation"][string_entity_relation_k] = entity_relation["is_good"]
    for event_mention_k, event_mentions in event_mention_k_to_event_mentions_annos_j.items():
        for event_mention in event_mentions:
            if event_mention["is_frozen"]:
                string_event_mention_k = "{}#{}".format("EventMention", "#".join(str(i) for i in event_mention_k))
                extraction_json_doc["annotation"][string_event_mention_k] = event_mention["is_good"]
    for event_arg_k, event_args in event_arg_k_to_event_args_annos_j.items():
        for event_arg in event_args:
            if event_arg["is_frozen"]:
                string_event_arg_k = "{}#{}".format("EventArg", "#".join(str(i) for i in event_arg_k))
                extraction_json_doc["annotation"][string_event_arg_k] = event_arg["is_good"]

    # Use the entries to repopulate UI display plus generate statistics
    mention_id_to_mention_extract, mention_id_to_sentence_extract, event_mention_id_to_event_mention_extract, event_mention_id_to_sentence_extract = build_json_id_to_json_entries(
        extraction_json_doc)
    mention_k_to_mentions_extracts_j, entity_relation_k_to_entity_relations_extracts_j, event_mention_k_to_event_mentions_extracts_j, event_arg_k_to_event_args_extracts_j = build_customer_k_to_objects(
        extraction_json_doc, mention_id_to_mention_extract, mention_id_to_sentence_extract,
        event_mention_id_to_event_mention_extract, event_mention_id_to_sentence_extract)
    for mention_k, mentions in mention_k_to_mentions_extracts_j.items():
        string_mention_k = "{}#{}".format("Mention", "#".join(str(i) for i in mention_k))
        if string_mention_k in extraction_json_doc["annotation"]:
            for mention in mentions:
                mention["is_frozen"] = True
                mention["is_good"] = extraction_json_doc["annotation"][string_mention_k]
    for entity_relation_k, entity_relations in entity_relation_k_to_entity_relations_extracts_j.items():
        string_entity_relation_k = "{}#{}".format("EntityRelation", "#".join(str(i) for i in entity_relation_k))
        if string_entity_relation_k in extraction_json_doc["annotation"]:
            for mention in entity_relations:
                mention["is_frozen"] = True
                mention["is_good"] = extraction_json_doc["annotation"][string_entity_relation_k]
    for event_mention_k, event_mentions in event_mention_k_to_event_mentions_extracts_j.items():
        string_event_mention_k = "{}#{}".format("EventMention", "#".join(str(i) for i in event_mention_k))
        if string_event_mention_k in extraction_json_doc["annotation"]:
            for mention in event_mentions:
                mention["is_frozen"] = True
                mention["is_good"] = extraction_json_doc["annotation"][string_event_mention_k]
    for event_arg_k, event_args in event_arg_k_to_event_args_extracts_j.items():
        string_event_arg_k = "{}#{}".format("EventArg", "#".join(str(i) for i in event_arg_k))
        if string_event_arg_k in extraction_json_doc["annotation"]:
            for mention in event_args:
                mention["is_frozen"] = True
                mention["is_good"] = extraction_json_doc["annotation"][string_event_arg_k]


# def merge_annotation_json_into_extraction(annotation_json, extraction):
#     performance_counter = {
#         "mentions": {
#             "positive_span_annotated": 0,
#             "positive_span_in_result": 0,
#             "negative_span_annotated": 0,
#             "negative_span_in_result": 0
#         },
#         "entity_relations": {
#             "positive_span_annotated": 0,
#             "positive_span_in_result": 0,
#             "negative_span_annotated": 0,
#             "negative_span_in_result": 0
#         },
#         "event_mentions": {
#             "positive_span_annotated": 0,
#             "positive_span_in_result": 0,
#             "negative_span_annotated": 0,
#             "negative_span_in_result": 0
#         },
#         "event_args": {
#             "positive_span_annotated": 0,
#             "positive_span_in_result": 0,
#             "negative_span_annotated": 0,
#             "negative_span_in_result": 0
#         }
#     }
#     # annotation front
#     mention_id_to_mention_anno_j, mention_id_to_sentence_anno_j, event_mention_id_to_event_mention_anno_j, event_mention_id_to_sentence_anno_j = build_json_id_to_json_entries(
#         annotation_json)
#     mention_k_to_mentions_anno_j, entity_relation_k_to_entity_relations_anno_j, event_mention_k_to_event_mentions_anno_j, event_arg_k_to_event_args_anno_j = build_customer_k_to_objects(
#         annotation_json, mention_id_to_mention_anno_j, mention_id_to_sentence_anno_j,
#         event_mention_id_to_event_mention_anno_j, event_mention_id_to_sentence_anno_j)
#     # extraction front
#     mention_id_to_mention_extraction_j, mention_id_to_sentence_extraction_j, event_mention_id_to_event_mention_extraction_j, event_mention_id_to_sentence_extraction_j = build_json_id_to_json_entries(
#         extraction)
#     mention_k_to_mentions_extraction_j, entity_relation_k_to_entity_relations_extraction_j, event_mention_k_to_event_mentions_extraction_j, event_arg_k_to_event_args_extraction_j = build_customer_k_to_objects(
#         extraction, mention_id_to_mention_extraction_j, mention_id_to_sentence_extraction_j,
#         event_mention_id_to_event_mention_extraction_j, event_mention_id_to_sentence_extraction_j)
#
#     unseen_mention_k_to_mention = dict()
#
#     # mention
#     for mention_k, mention_annos_j in mention_k_to_mentions_anno_j.items():
#         if mention_k not in mention_k_to_mentions_extraction_j:
#             # We have to preserve these otherwise it may be an issue if we marked some event_arg but lost progress later
#             for mention_anno_j in mention_annos_j:
#                 mention_anno_j["should_display"] = False
#                 _, sent_no, _, _, _ = mention_k
#                 extraction["sentences"][sent_no]["mentions"].append(mention_anno_j)
#                 unseen_mention_k_to_mention.setdefault(mention_k, list()).append(mention_anno_j)
#         else:
#             golden_annos = list(filter(lambda x: x["is_frozen"] is True, mention_k_to_mentions_anno_j[mention_k]))
#             if len(golden_annos) > 0:
#                 for m in mention_k_to_mentions_extraction_j[mention_k]:
#                     m["is_frozen"] = True
#                     m["is_good"] = golden_annos[0]["is_good"]
#
#     joint_mention_k_to_mention_extraction_j = dict()
#     for mention_k, ens in mention_k_to_mentions_extraction_j.items():
#         joint_mention_k_to_mention_extraction_j.setdefault(mention_k, list()).extend(ens)
#     for mention_k, ens in unseen_mention_k_to_mention.items():
#         joint_mention_k_to_mention_extraction_j.setdefault(mention_k, list()).extend(ens)
#
#     # entity_relation
#     for entity_relation_k, entity_relation_annos_j in entity_relation_k_to_entity_relations_anno_j.items():
#         if entity_relation_k not in entity_relation_k_to_entity_relations_extraction_j:
#             for entity_relation_anno_j in entity_relation_annos_j:
#                 entity_relation_anno_j["should_display"] = False
#                 _,old_left_mention_k,old_right_mention_k,_ = entity_relation_k
#                 new_mention_left = joint_mention_k_to_mention_extraction_j[old_left_mention_k][0]
#                 new_mention_right = joint_mention_k_to_mention_extraction_j[old_right_mention_k][0]
#                 entity_relation_anno_j["left_mention_id"] = new_mention_left["mention_id"]
#                 entity_relation_anno_j["right_mention_id"] = new_mention_right["mention_id"]
#                 extraction["entity_relations"].append(entity_relation_anno_j)
#         else:
#             golden_annos = list(filter(lambda x: x["is_frozen"] is True,
#                                        entity_relation_k_to_entity_relations_anno_j[entity_relation_k]))
#             if len(golden_annos) > 0:
#                 for m in entity_relation_k_to_entity_relations_extraction_j[entity_relation_k]:
#                     m["is_frozen"] = True
#                     m["is_good"] = golden_annos[0]["is_good"]
#
#     unseen_event_mention_k_to_event_mention = dict()
#
#     # event_mention
#     for event_mention_k, event_mention_annos_j in event_mention_k_to_event_mentions_anno_j.items():
#         if event_mention_k not in event_mention_k_to_event_mentions_extraction_j:
#             # We have to preserve these otherwise it may be an issue if we marked some event_arg but lost progress later
#             for event_mention_anno_j in event_mention_annos_j:
#                 event_mention_anno_j["should_display"] = False
#                 _, sent_no, _, _, _ = event_mention_k
#                 extraction["sentences"][sent_no]["event_mentions"].append(event_mention_anno_j)
#                 unseen_event_mention_k_to_event_mention.setdefault(event_mention_k, list()).append(event_mention_anno_j)
#         else:
#             golden_annos = list(
#                 filter(lambda x: x["is_frozen"] is True, event_mention_k_to_event_mentions_anno_j[event_mention_k]))
#             if len(golden_annos) > 0:
#                 for m in event_mention_k_to_event_mentions_extraction_j[event_mention_k]:
#                     m["is_frozen"] = True
#                     m["is_good"] = golden_annos[0]["is_good"]
#
#     joint_event_mention_k_to_event_mention_extraction_j = dict()
#     for event_mention_k, ens in event_mention_k_to_event_mentions_extraction_j.items():
#         joint_event_mention_k_to_event_mention_extraction_j.setdefault(event_mention_k, list()).extend(ens)
#     for event_mention_k, ens in unseen_event_mention_k_to_event_mention.items():
#         joint_event_mention_k_to_event_mention_extraction_j.setdefault(event_mention_k, list()).extend(ens)
#
#     # event_arg
#     for event_arg_k, event_arg_annos_j in event_arg_k_to_event_args_anno_j.items():
#         if event_arg_k not in event_arg_k_to_event_args_extraction_j:
#             for event_arg_anno_j in event_arg_annos_j:
#                 event_arg_anno_j["should_display"] = False
#                 _, event_mention_key, mention_key, _ = event_arg_k
#                 new_event_mention_left = joint_event_mention_k_to_event_mention_extraction_j[event_mention_key][0]
#                 new_mention_right = joint_mention_k_to_mention_extraction_j[mention_key][0]


def create_app():
    logging.basicConfig(level=logging.getLevelName(os.environ.get('LOGLEVEL', 'INFO').upper()),
                        format='[%(asctime)s] {P%(process)d:%(module)s:%(lineno)d} %(levelname)s - %(message)s')

    flask_app = flask.Flask(__name__, static_folder=os.path.join(project_root, "backend/statics"),
                            static_url_path='')
    flask_cors.CORS(flask_app)

    # default_text = "Billy Mays, the bearded, boisterous pitchman who, as the undisputed king of TV yell and sell, became an unlikely pop culture icon, died at his home in Tampa, Fla, on Sunday."
    # default_marked_text = "[[John Smith|Mention|PERSON]], a great man, [[died|EventMention|Death]] in [[Florida|Mention|LOCATION]]."
    default_original_text = "John Smith, a great man, died in Florida."
    default_original_text = "Billy Mays, the bearded, boisterous pitchman who, as the undisputed king of TV yell and sell, became an unlikely pop culture icon, died at his home in Tampa, Fla, on Sunday."
    default_extraction = dict()
    default_serifxml = ""

    @flask_app.after_request
    def add_header(r):
        """
        Add headers to both force latest IE rendering engine or Chrome Frame,
        and also to cache the rendered page for 10 minutes.
        """
        r.headers["Cache-Control"] = "public, no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
        r.headers['Last-Modified'] = datetime.datetime.now()
        r.headers["Pragma"] = "no-cache"
        r.headers["Expires"] = "-1"
        r.headers['Cache-Control'] = 'public, max-age=0'
        return r

    # PySerif basic
    pyserif_basic_config_path = os.path.join(project_root, "backend/config_a2t_basic_nlp.yml")
    with open(pyserif_basic_config_path) as fp:
        pyserif_basic_config = yaml.full_load(fp)
    argparse_ins = DuckClass()
    argparse_ins.PRODUCTION_MODE = False
    models, model_name_to_cls = assemble_pipeline(pyserif_basic_config, argparse_ins)
    pyserif_nlp_basic_pipeline = PySerifPipeline(lang="English")
    pyserif_nlp_basic_pipeline.set_models(models)
    # Pyserif basic end

    # A2TModel
    a2t_default_config_path = os.path.join(project_root, "backend/default_config.json")
    with open(a2t_default_config_path) as fp:
        a2t_default_config_dict = json.load(fp)
    a2t_driver = A2TDriver()

    @flask_app.before_first_request
    def flask_warmup():
        nonlocal a2t_driver
        nonlocal pyserif_nlp_basic_pipeline
        nonlocal default_original_text
        nonlocal default_extraction
        nonlocal default_serifxml
        logger.info("Loading PySerif basic models")
        pyserif_nlp_basic_pipeline.load_models()
        logger.info("Loading A2T models")
        a2t_driver.load_model()
        logger.info("Produce default extraction")
        a2t_driver.parse_template(a2t_default_config_dict)
        serif_docs = pyserif_nlp_basic_pipeline.process_txts({"doc_1": default_original_text})
        a2t_driver.process_document(serif_docs[0])
        final_serif_doc = serif_docs[0]

        default_serifxml = serifxml_to_string(final_serif_doc)

    @flask_app.route("/process_text", methods=["POST"])
    def process_text():
        original_text = flask.request.json.get("original_text")
        a2t_template_dict = flask.request.json.get("a2t_template", None)
        if a2t_template_dict is None:
            a2t_template_dict = a2t_default_config_dict
        a2t_driver.parse_template(a2t_template_dict)
        serif_docs = pyserif_nlp_basic_pipeline.process_txts({"doc_1": original_text})
        a2t_driver.process_document(serif_docs[0])
        return flask.jsonify(
            {"extraction": serif_json_seralizer(serif_docs[0]), "serif_doc": serifxml_to_string(serif_docs[0])}), 200

    @flask_app.route("/process_marked_text", methods=["POST"])
    def process_marked_text():
        marked_text = flask.request.json.get("marked_text")
        a2t_template_dict = flask.request.json.get("a2t_template", None)
        if a2t_template_dict is None:
            a2t_template_dict = a2t_default_config_dict
        a2t_driver.parse_template(a2t_template_dict)
        original_text, spans = convert_marked_text_into_plain_text_and_markings(marked_text)
        serif_docs = pyserif_nlp_basic_pipeline.process_txts({"doc_1": original_text})
        add_spans_into_serifxml(serif_docs[0], spans)
        a2t_driver.process_document(serif_docs[0])
        return flask.jsonify(
            {"extraction": serif_json_seralizer(serif_docs[0]), "serif_doc": serifxml_to_string(serif_docs[0])}), 200

    @flask_app.route("/process_serifxml", methods=["POST"])
    def process_serifxml():
        original_serifxml_f = flask.request.files.get("original_serifxml")
        original_a2t_template_dict = flask.request.files.get("a2t_template", None)
        if original_a2t_template_dict is not None:
            a2t_template_dict = json.loads(original_a2t_template_dict.read().decode("utf-8"))
        else:
            a2t_template_dict = a2t_default_config_dict
        serif_doc = Document(original_serifxml_f.read().decode("utf-8"))
        a2t_driver.parse_template(a2t_template_dict)
        a2t_driver.process_document(serif_doc)
        return flask.jsonify(
            {"extraction": serif_json_seralizer(serif_doc), "serif_doc": serifxml_to_string(serif_doc)}), 200

    @flask_app.route("/default_a2t_template", methods=["GET"])
    def get_default_a2t_template():
        return flask.jsonify(
            {"default_a2t_template": a2t_default_config_dict, "default_original_text": default_original_text,
             "default_extraction": default_extraction, "default_serif_doc": default_serifxml}), 200

    @flask_app.route("/replace_default_a2t_template", methods=["POST"])
    def replace_default_a2t_template():
        nonlocal a2t_default_config_dict
        a2t_template_dict = flask.request.json.get("a2t_template", None)
        if a2t_template_dict != None:
            a2t_default_config_dict = a2t_template_dict
        return flask.jsonify({"status": "OK"}), 200

    @flask_app.route("/process_raw_text_basic_nlp", methods=["POST"])
    def process_raw_text_basic_nlp():
        original_text = flask.request.json.get("original_text")
        serif_docs = pyserif_nlp_basic_pipeline.process_txts({"doc_1": original_text})
        return flask.jsonify(
            {"extraction": serif_json_seralizer(serif_docs[0]), "serif_doc": serifxml_to_string(serif_docs[0])}), 200

    @flask_app.route("/process_markup_sentence_throgh_a2t", methods=["POST"])
    def process_markup_sentence_through_a2t():
        original_doc_dict = flask.request.json.get("original_doc_dict")
        original_serif_doc = flask.request.json.get("original_serif_doc")
        serif_doc = Document(original_serif_doc)
        modify_serifxml_from_unary_markings(serif_doc, original_doc_dict)
        a2t_template_dict = flask.request.json.get("a2t_template", None)
        if a2t_template_dict is None:
            a2t_template_dict = a2t_default_config_dict
        a2t_driver.parse_template(a2t_template_dict)
        a2t_driver.process_document(serif_doc)
        return flask.jsonify(
            {"extraction": serif_json_seralizer(serif_doc), "serif_doc": serifxml_to_string(serif_doc)}), 200

    @flask_app.route("/heuristic_te", methods=["GET"])
    def heuristic_te():
        pass

    @flask_app.route("/rescore_a2t_template", methods=["POST"])
    def rescore_using_latest_template():
        a2t_template_dict = flask.request.json.get("a2t_template", None)
        if a2t_template_dict is None:
            a2t_template_dict = a2t_default_config_dict
        adjudicated_extraction = flask.request.json.get("a2t_extraction", dict())
        unary_marking_extraction = flask.request.json.get("step_1_marking_extraction")
        step_1_serifxml = flask.request.json.get("step_1_serifxml")
        serif_doc = Document(step_1_serifxml)
        modify_serifxml_from_unary_markings(serif_doc, unary_marking_extraction)
        a2t_driver.parse_template(a2t_template_dict)
        a2t_driver.process_document(serif_doc)
        new_extraction = serif_json_seralizer(serif_doc)
        resolve_annotation(adjudicated_extraction, new_extraction)
        return flask.jsonify(
            {"extraction": new_extraction, "serif_doc": serifxml_to_string(serif_doc)}), 200

    return flask_app


if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(host='::', port=5008)
