# Copyright 2019 by Raytheon BBN Technologies Corp.
# All Rights Reserved.
import os, sys, logging, copy
import pickle
logger = logging.getLogger(__name__)

current_script_path = __file__
project_root = os.path.realpath(os.path.join(current_script_path, os.path.pardir, os.path.pardir, os.path.pardir))
sys.path.append(project_root)

import argparse
import importlib
import os
import sys
import datetime
import json
import io
import numpy as np

from serif import Document
import time
import flask
from flask_cors import CORS

class PySerifProcessor(object):
    def __init__(self,args):
        self.args = args

    def process(self,serif_doc:Document,aux:dict)-> Document:
        serif_docs = [serif_doc]
        intermediate_output_doc_list = serif_docs
        for model_seq in self.args.models: # iterate over the number of model sequences to apply
            intermediate_input_doc_list = intermediate_output_doc_list
            intermediate_output_doc_list = []
            for i, document in enumerate(intermediate_input_doc_list):
                logger.info('Processing: Begin {}'.format(document.docid))
                for model, _ in model_seq:
                    document.aux = copy.deepcopy(aux)
                    ret = model.process(document)
                    logger.info('Processing: Applying {}'.format(type(model).__name__))
                    if isinstance(ret, Document):
                        document = ret
                intermediate_output_doc_list.append(document)
                logger.info('Processing: End {}'.format(document.docid))
            return intermediate_output_doc_list[0]

def read_config(arguments):
    """
    Adapted from HUME
    :param arguments:
    """
    models = []
    model_seq = []
    class_name_to_class = dict()
    implementations_path = ''

    model_types = [
        'BASE_MODEL',
        'JAVA_BASE_MODEL',
        'SENTENCE_SPLITTING_MODEL',
        'TOKENIZE_MODEL',
        'PART_OF_SPEECH_MODEL',
        'DEPENDENCY_MODEL',
        'PARSE_MODEL',
        'NAME_MODEL',
        'MENTION_MODEL',
        'RELATION_MENTION_MODEL',
        'EVENT_MENTION_MODEL',
        'ENTITY_MODEL',
        'RELATION_MODEL',
        'EVENT_MODEL',
        'EVENT_EVENT_RELATION_MENTION_MODEL'
    ]

    config_path = os.path.abspath(arguments.config)
    with open(config_path, 'r') as f:
        for line in f:
            line = line.strip()
            # comment or empty
            if len(line) == 0 or line.startswith('#'):
                continue

            # location of user-specified model implementations
            if line.startswith('IMPLEMENTATIONS'):
                implementations_path = os.path.realpath(next(f).strip())
                parent, filename = os.path.split(implementations_path)
                _, package_name = os.path.split(parent)
                module_name = os.path.splitext(filename)[0]
                # inserting at 1 allows implementation to import abstract class
                sys.path.insert(1, parent)
                try:
                    implementations = importlib.import_module(
                        module_name, package=package_name)
                    for cls_name in dir(implementations):
                        if cls_name not in class_name_to_class:
                            class_name_to_class[cls_name] = getattr(implementations,cls_name)
                except ImportError as e:
                    logger.critical('Implementations at {} could not be imported; '
                                    'make sure that the file exists and is a python '
                                    'module (sister to an __init__.py file).'
                                    .format(os.path.join(parent, filename)))
                    raise e
                continue
            if line.startswith('JAVA_CLASSPATH'):
                java_class_path = os.path.realpath(next(f).strip())
                l = set(os.environ.get("CLASSPATH","").split(":"))
                l.discard("")
                l.add(java_class_path)
                os.environ['CLASSPATH'] = ":".join(l)
                continue


            # Set up a model
            model_line = False
            is_barrier = False
            for model_type in model_types:
                if line.startswith(model_type + ' '):
                    model_line = True
                    model_line_split = line.split()
                    model_classname = model_line_split[1]
                    if (len(model_line_split) >= 3) and (model_line_split[2] == 'BARRIER'): # check if model is a barrier
                        is_barrier = True
                    try:
                        _Model = class_name_to_class[model_classname]
                        # _Model = getattr(implementations, model_classname)
                    except KeyError as e:
                        logger.critical("No " + model_type + " subclass {} could be found at {}"
                                        .format(model_classname, implementations_path))
                        raise e
                    else:
                        model_seq.append((_Model, {}, is_barrier))

                        if is_barrier:
                            models.append(model_seq)
                            model_seq = list()
                        break
            if model_line:
                continue

            # Not an implementation or model line, read kwarg
            # the last model in model_seq should be updated, unless it's a barrier
            # (in which case model_seq is empty and the barrier model is at the end of the last model_seq inside models)
            if model_seq:
                last_model_kwargs = model_seq[-1][1]
            else:
                last_model_kwargs = models[-1][-1][1]
            kwarg_info = line.split()
            kwarg = kwarg_info[0]
            if len(kwarg_info) == 1:  # boolean
                last_model_kwargs[kwarg] = True
            elif len(kwarg_info) == 2:  # keyword and arg
                last_model_kwargs[kwarg_info[0]] = kwarg_info[1]
            else:
                raise IOError(
                    'Config file model {} parameter "{}" should consist of '
                    'the name of the keyword and up to one value; got '
                    'these values: {}'
                        .format(model_seq[-1][0].__name__, line, kwarg_info[1:]))

    # if no barrier exists at the end of the current model_seq,
    # the model_seq list will be non-empty and must be added to models
    if model_seq:
        models.append(model_seq)

    for model_seq in models:
        for _, kwargs, _ in model_seq:
            kwargs['argparse'] = arguments

    final_models = []
    for idx, model_seq in enumerate(models):
        final_models.append(list())
        for m, kwargs, is_barrier in model_seq:
            final_models[idx].append((m(**kwargs), is_barrier))
    # models = [m(**kwargs) for m, kwargs in models]

    arguments.implementations = implementations
    arguments.models = final_models


def parse(args_list):
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('config')
    _args = arg_parser.parse_args(args_list)
    read_config(_args)
    return _args

def create_flask_app():
    args = parse(sys.argv[1:])
    pyserif_processor = PySerifProcessor(args)
    flask_app = flask.Flask(__name__)
    CORS(flask_app)

    @flask_app.errorhandler(Exception)
    def internal_server_error(error):
        from traceback import format_exc, print_exc
        flask.current_app.logger.error(json.dumps({'msg': format_exc(), 'msg_type': "500"}))
        if flask_app.config.get('DEBUG') is True:
            print_exc()
        return flask.jsonify({'text': format_exc()}), 500

    # @flask_app.before_first_request
    # def preheat_models():
    #     pyserif_processor.process(Document(os.path.join(project_root,"test","sample_doc.xml")),dict())

    @flask_app.before_first_request
    def preheat_models():
        for model_seq in args.models: # iterate over the number of model sequences to apply
            for model,_ in model_seq:
                model.reload_model()

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

    @flask_app.route('/v1/process_serifxml',methods=['POST'])
    def process_serifxml():
        try:
            serifxml_str = flask.request.files['serifxml'].read()
            if isinstance(serifxml_str, bytes):
                serifxml_str = serifxml_str.decode('utf-8')
            aux = dict()
            if flask.request.files.get("aux"):
                aux = pickle.load(flask.request.files.get("aux"))

        except:
            import traceback
            traceback.print_exc()
            return flask.jsonify({'status': 'ERROR', 'msg': traceback.format_exc()}), 500
        try:
            serif_doc = Document(serifxml_str)
            processed_doc = pyserif_processor.process(serif_doc,aux)
            return_buf = io.BytesIO()
            processed_doc.save(return_buf)
            return_buf.seek(0)
            return flask.send_file(return_buf,attachment_filename="{}.xml".format(processed_doc.docid),mimetype="application/xml")
        except:
            import traceback
            traceback.print_exc()
            return flask.jsonify({'status': 'ERROR', 'msg': traceback.format_exc()}), 500
    return flask_app


if __name__ == '__main__':
    log_format = '[%(asctime)s] {P%(process)d:%(module)s:%(lineno)d} %(levelname)s - %(message)s'
    try:
        logging.basicConfig(level=logging.getLevelName(os.environ.get('LOGLEVEL', 'INFO').upper()),
                            format=log_format)
    except ValueError as e:
        logging.error(
            "Unparseable level {}, will use default {}.".format(os.environ.get('LOGLEVEL', 'INFO').upper(),
                                                                logging.root.level))
        logging.basicConfig(format=log_format)
    app = create_flask_app()
    app.run(host="0.0.0.0")
