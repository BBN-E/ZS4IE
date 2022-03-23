import axios from "axios";
import constants from "@/constants/main";

export default {
  processText(originalText, a2tTemplate) {
    return axios({
      baseURL: constants.baseURL,
      url: "/process_text",
      method: "POST",
      data: {
        original_text: originalText,
        a2t_template: a2tTemplate,
      },
    });
  },
  getDefaultA2TTemplate() {
    return axios({
      baseURL: constants.baseURL,
      url: "/default_a2t_template",
      method: "GET",
    });
  },
  processSerifXML(formData) {
    return axios({
      baseURL: constants.baseURL,
      url: "/process_serifxml",
      method: "POST",
      data: formData,
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
  },
  processMarkedText(markedText, a2tTemplate) {
    return axios({
      baseURL: constants.baseURL,
      url: "/process_marked_text",
      method: "POST",
      data: {
        marked_text: markedText,
        a2t_template: a2tTemplate,
      },
    });
  },
  processOriginalTextStep0(originalText) {
    return axios({
      baseURL: constants.baseURL,
      url: "/process_raw_text_basic_nlp",
      method: "POST",
      data: {
        original_text: originalText,
      },
    });
  },
  processMarkedTextStep1(originalSeriXML, jsonDoc, a2tTemplate) {
    return axios({
      baseURL: constants.baseURL,
      url: "/process_markup_sentence_throgh_a2t",
      method: "POST",
      data: {
        original_doc_dict: jsonDoc,
        original_serif_doc: originalSeriXML,
        a2t_template: a2tTemplate,
      },
    });
  },
  scoreDocument(annotationEntry, a2tTemplate) {
    return axios({
      baseURL: constants.baseURL,
      url: "/rescore_a2t_template",
      method: "POST",
      data: {
        a2t_template: a2tTemplate,
        a2t_extraction: annotationEntry.a2t_extraction,
        step_1_marking_extraction: annotationEntry.step_1_marking_extraction,
        step_1_serifxml: annotationEntry.step_1_serifxml,
      },
    });
  },
};
