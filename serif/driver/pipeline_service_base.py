"""
This is for providing a flexible lifecycle hooks for implement model persistence as well as potential online decoding.
"""

import importlib
import logging
import os
import sys
import yaml

logger = logging.getLogger(__name__)
current_script_path = __file__
project_root = os.path.realpath(os.path.join(current_script_path, os.path.pardir, os.path.pardir, os.path.pardir))
sys.path.append(project_root)

from serifxml3 import Document


class DuckClass(object):
    pass


def assemble_pipeline(config_dict, argparse=None):
    for java_classpath in config_dict.get("class_loader_paths", dict()).get("java"):
        l = list(os.environ.get("CLASSPATH", "").split(":"))
        l = list(filter(lambda a: a != "", l))
        l = [java_classpath] + l
        os.environ['CLASSPATH'] = ":".join(l)
    model_name_to_cls = dict()
    for implementations_path in config_dict.get("class_loader_paths", dict()).get("python"):
        parent, filename = os.path.split(implementations_path)
        _, package_name = os.path.split(parent)
        module_name = os.path.splitext(filename)[0]
        # inserting at 1 allows implementation to import abstract class
        sys.path.insert(1, parent)
        implementations = importlib.import_module(
            module_name, package=package_name)
        for cls_name in dir(implementations):
            if cls_name not in model_name_to_cls:
                model_name_to_cls[cls_name] = getattr(implementations, cls_name)
            else:
                logger.warning("{} has been imported. Ignoring {}.{}".format(cls_name, implementations_path, cls_name))
    models = list()
    for model_config in config_dict.get("models", ()):
        model_name = model_config["model_name"]
        kwargs = model_config["kwargs"]
        model_ins = model_name_to_cls[model_name](**kwargs)
        model_ins.argparse = argparse
        models.append(model_ins)
    if argparse is not None:
        argparse.models = models
        argparse.implementations = model_name_to_cls
    return models, model_name_to_cls


class PySerifPipeline(object):
    def __init__(self, lang):
        self.lang = lang
        self.models = list()

    def load_models(self):
        for model in self.models:
            model.load_model()

    def unload_models(self):
        for model in self.models:
            model.unload_model()

    def set_models(self, models):
        self.models = models

    def clear_models(self):
        self.models = []

    def process_serif_docs(self, serif_docs):
        for i, model in enumerate(self.models):
            logger.info('Processing: Applying {}'.format(type(model).__name__))
            serif_docs = model.apply(serif_docs)
        return serif_docs

    def process_txts(self, doc_id_to_txt):
        serif_docs = list()
        for doc_id, text in doc_id_to_txt.items():
            serif_doc = Document.from_string(text, self.lang, doc_id)
            serif_docs.append(serif_doc)
        return self.process_serif_docs(serif_docs)


def batch_processing_test():
    config_path = "/nfs/raid88/u10/users/hqiu_ad/repos/text-open/src/python/config/config_a2t_basic_nlp.yml"
    output_path = "/home/hqiu/tmp/"
    input_txt = dict()
    with open("/nfs/raid88/u10/users/hqiu_ad/repos/text-open/src/python/test/sample_doc.txt") as fp:
        for idx, i in enumerate(fp):
            i = i.strip()
            if len(i) > 1:
                input_txt["doc_{}".format(idx)] = i
    input_txt["doc_1"] = "Billy Mays, the bearded, boisterous pitchman who, as the undisputed king of TV yell and sell, became an unlikely pop culture icon, died at his home in Tampa, Fla, on Sunday."
    pyserif_pipeline = PySerifPipeline(lang="English")
    with open(config_path) as fp:
        config_dict = yaml.full_load(fp)
    argparse_ins = DuckClass()
    argparse_ins.PRODUCTION_MODE = False
    models, model_name_to_cls = assemble_pipeline(config_dict, argparse_ins)
    pyserif_pipeline.set_models(models)
    pyserif_pipeline.load_models()
    serif_docs = pyserif_pipeline.process_txts(input_txt)
    for serif_doc in serif_docs:
        serif_doc.save(os.path.join(output_path, "{}.xml".format(serif_doc.docid)))


if __name__ == "__main__":
    batch_processing_test()
