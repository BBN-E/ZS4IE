// const baseURL = "http://127.0.0.1:5008";
const baseURL = "";
const spanStyles = {
  binary_relation: {
    slot_0: {
      "background-color": "lightblue",
      "border-bottom": "2px solid blue",
    },
    slot_1: {
      "background-color": "lightgreen",
      "border-top": "2px solid green",
    },
  },
  unary: {
    cluster1: { "background-color": "#F8BBD0" },
    cluster2: { "background-color": "#E1BEE7" },
    cluster3: { "background-color": "#D1C4E9" },
    cluster4: { "background-color": "#C5CAE9" },
    cluster5: { "background-color": "#BBDEFB" },
    cluster6: { "background-color": "#B3E5FC" },
    cluster7: { "background-color": "#B2EBF2" },
    cluster8: { "background-color": "#B2DFDB" },
    cluster10: { "background-color": "#DCEDC8" },
    cluster11: { "background-color": "#F0F4C3" },
    cluster12: { "background-color": "#FFF9C4" },
    cluster13: { "background-color": "#FFECB3" },
    cluster14: { "background-color": "#FFE0B2" },
    cluster15: { "background-color": "#FFCCBC" },
    cluster16: { "background-color": "#D7CCC8" },
    cluster17: { "background-color": "#CFD8DC" },
  },
  focus_token: {
    "border-bottom": "2px solid #cc3600",
  },
  selected_token: {
    "background-color": "#ffc7b3",
  },
};
const exampleExtraction = {
  doc_id: "doc_1",
  entity_relations: [],
  event_mention_id_to_event_mention_loc: {},
  mention_id_to_mention_loc: {},
  sentences: [],
};
export default {
  baseURL: baseURL,
  spanStyles: spanStyles,
  exampleExtraction: exampleExtraction,
};
