import os, json, yaml

current_script_path = __file__
project_root = os.path.realpath(
    os.path.join(current_script_path, os.path.pardir, os.path.pardir, os.path.pardir, os.path.pardir, os.path.pardir))


import serifxml3
from serif.driver.pipeline_service_base import PySerifPipeline, DuckClass, assemble_pipeline
from serif.model.impl.a2t_adapter.special_text_parser import event_arg_sentence_to_marking

from serif.model.impl.a2t_adapter.A2TDriver import A2TDriver
def main():
    config_path = os.path.join(project_root, "config/config_a2t_basic_nlp.yml")
    pyserif_nlp_basic_pipeline = PySerifPipeline(lang="English")
    with open(config_path) as fp:
        config_dict = yaml.full_load(fp)
    argparse_ins = DuckClass()
    argparse_ins.PRODUCTION_MODE = False
    # models, model_name_to_cls = assemble_pipeline(config_dict, argparse_ins)
    # pyserif_nlp_basic_pipeline.set_models(models)
    # pyserif_nlp_basic_pipeline.load_models()

    with open(os.path.join(project_root, "serif/model/impl/a2t_adapter/default_config_event_arg_heuristic.json")) as fp:
        a2t_config = json.load(fp)
    a2t_driver = A2TDriver()
    # a2t_driver.load_model()
    a2t_driver.parse_template(a2t_config)

    granular_serif_list = "/nfs/raid88/u10/users/skandula-ad/expts/templateslot_candidate/train/pred+gold_fillers.serif.list"
    serif_docs = list()
    with open(granular_serif_list) as fp:
        for idx,i in enumerate(fp):
            i = i.strip()
            serif_doc = serifxml3.Document(i)
            serif_docs.append(serif_doc)
            # if idx > 5:
            #     break
    annotation_examples = a2t_driver.prepopulate_annotation_sentences(serif_docs)
    for annotation_example in annotation_examples:
        original_example, matched_examples = annotation_example
        print("################################")
        print(event_arg_sentence_to_marking(original_example[0],original_example[1]))
        for matched_example in matched_examples:
            print(event_arg_sentence_to_marking(matched_example[0],matched_example[1]))


if __name__ == "__main__":
    main()