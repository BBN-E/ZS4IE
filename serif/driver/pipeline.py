import argparse
import importlib
import logging
import os
import sys

from serif.model.ingester import Ingester

logger = logging.getLogger(__name__)

current_script_path = __file__
project_root = os.path.realpath(os.path.join(current_script_path, os.path.pardir, os.path.pardir, os.path.pardir))
sys.path.append(project_root)


def main(args):
    args.PRODUCTION_MODE = False
    if os.environ.get("PRODUCTION_MODE", "false").lower() == "true":
        args.PRODUCTION_MODE = True
        logger.critical("PRODUCTION MODE ON.")

    if not os.path.isdir(args.output_directory):
        os.makedirs(args.output_directory)

    files_to_process = []
    # Assume batch file
    i = open(args.input_file)
    for line in i:
        line = line.strip()
        if len(line) == 0 or line.startswith("#"):
            continue
        files_to_process.append(line)

    serif_docs = list()
    for idx, input_file_path in enumerate(files_to_process):
        logger.info("({}/{}) Ingesting: {}".format(idx + 1, len(files_to_process), input_file_path))
        ingester = args.models[0]
        documents = ingester.ingest(input_file_path)
        serif_docs.extend(documents)

    for i, model in enumerate(args.models[1:]):
        logger.info('Loading resources for {}'.format(type(model).__name__))
        model.load_model()
        logger.info('Processing: Applying {}'.format(type(model).__name__))
        serif_docs = model.apply(serif_docs)
        logger.info('Releasing resources for {}'.format(type(model).__name__))
        model.unload_model()

    for serif_doc in serif_docs:
        logger.info('Writing SerifXML file {}'.format(serif_doc.docid))
        filename = serif_doc.docid + ".xml"
        output_file = os.path.join(args.output_directory, filename)
        serif_doc.save(output_file)


def read_config(arguments):
    """
    Adapted from HUME
    :param arguments:
    """
    models = []
    class_name_to_class = dict()
    implementations_path = ''

    model_types = [
        'INGESTER',
        'BASE_MODEL',
        'JAVA_BASE_MODEL',
        'SENTENCE_SPLITTING_MODEL',
        'TOKENIZE_MODEL',
        'PART_OF_SPEECH_MODEL',
        'VALUE_MENTION_MODEL',
        'TIME_VALUE_MENTION_MODEL',
        'DEPENDENCY_MODEL',
        'PARSE_MODEL',
        'NAME_MODEL',
        'MENTION_MODEL',
        'ACTOR_MENTION_MODEL',
        'MENTION_COREF_MODEL',
        'EVENT_MENTION_COREF_MODEL',
        'RELATION_MENTION_MODEL',
        'EVENT_MENTION_MODEL',
        'ENTITY_MODEL',
        'VALUE_MODEL',
        'RELATION_MODEL',
        'EVENT_MODEL',
        'EVENT_EVENT_RELATION_MENTION_MODEL',
        'ACTOR_ENTITY_MODEL'
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
                            class_name_to_class[cls_name] = getattr(implementations, cls_name)
                except ImportError as e:
                    logger.critical('Implementations at {} could not be imported; '
                                    'make sure that the file exists and is a python '
                                    'module (sister to an __init__.py file).'
                                    .format(os.path.join(parent, filename)))
                    raise e
                continue
            if line.startswith('JAVA_CLASSPATH'):
                java_class_path = os.path.realpath(next(f).strip())
                l = set(os.environ.get("CLASSPATH", "").split(":"))
                l.discard("")
                l.add(java_class_path)
                os.environ['CLASSPATH'] = ":".join(l)
                continue

            # Set up a model
            model_line = False
            for model_type in model_types:
                if line.startswith(model_type + ' '):
                    model_line = True
                    model_line_split = line.split()
                    model_classname = model_line_split[1]

                    if model_type == 'INGESTER' and len(models) > 0:
                        raise IOError(
                            'Only one INGESTER should be specified and it must be '
                            'the first model listed')
                    try:
                        _Model = class_name_to_class[model_classname]
                        # _Model = getattr(implementations, model_classname)
                    except KeyError as e:
                        logger.critical("No " + model_type + " subclass {} could be found at {}"
                                        .format(model_classname, implementations_path))
                        raise e
                    else:
                        models.append((_Model, {}))
                        break
            if model_line:
                continue

            last_model_kwargs = models[-1][1]
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
                        .format(models[-1][0].__name__, line, kwarg_info[1:]))

    for model in models:
        for _, kwargs in models:
            kwargs['argparse'] = arguments

    arguments.models = [m(**kwargs) for m, kwargs in models]
    arguments.implementations = implementations
    config_logger()
    if not isinstance(arguments.models[0], Ingester):
        raise IOError(
            'First model in config file must be an Ingester '
            'for instance: "INGESTER SerifxmlIngester" or '
            'or "INGESTER TextIngester" followed by any arguments')


def parse(args_list):
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('config')
    arg_parser.add_argument('input_file')
    arg_parser.add_argument('output_directory')
    _args = arg_parser.parse_args(args_list)
    read_config(_args)
    return _args


def config_logger():
    # We need to run it twice due to some model may alter the behavior
    log_format = '[%(asctime)s] {P%(process)d:%(module)s:%(lineno)d} %(levelname)s - %(message)s'
    try:
        logging.basicConfig(level=logging.getLevelName(os.environ.get('LOGLEVEL', 'INFO').upper()),
                            format=log_format)
    except ValueError as e:
        logging.error(
            "Unparseable level {}, will use default {}.".format(os.environ.get('LOGLEVEL', 'INFO').upper(),
                                                                logging.root.level))
        logging.basicConfig(format=log_format)


if __name__ == '__main__':
    config_logger()
    main(parse(sys.argv[1:]))
