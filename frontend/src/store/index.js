import Vue from "vue";
import Vuex from "vuex";
import service from "@/service/main";
import _ from "lodash";
import constants from "@/constants/main";
Vue.use(Vuex);

const resolveOntology = (originalDict) => {
  const resolvedOntology = [];
  for (const [ontologyName, ontologyProperty] of Object.entries(
    originalDict.ontology
  )) {
    ontologyProperty.ontologyName = ontologyName;
    if (!("input_constraints" in ontologyProperty))
      ontologyProperty.input_constraints = [];
    if (!("use_global_input_constraints" in ontologyProperty))
      ontologyProperty.use_global_input_constraints = false;
    resolvedOntology.push(ontologyProperty);
  }
  originalDict.ontology = resolvedOntology;
};
const recoverOntology = (originalDict) => {
  const reolvedOntology = {};
  for (const ontologyEn of originalDict.ontology) {
    reolvedOntology[ontologyEn.ontologyName] = ontologyEn;
  }
  originalDict.ontology = reolvedOntology;
};

const defaultFocusTaskEntry = {
  ontology: [],
  input_constraints: [],
};

const defaultTypeEntry = {
  ontologyName: "",
  input_constraints: [],
  templates: [],
  use_global_input_constraints: false,
};

export default new Vuex.Store({
  state: {
    NERConfig: {},
    entityRelationConfig: {},
    eventConfig: {},
    eventArgConfig: {},
    stagesToRun: [],
    displayOntologyPanel: false,
    focusTaskEntry: defaultFocusTaskEntry,
    ontologyContraintPanelOpened: false,
    ontologyContraintPanelFocusGlobalConstraint: false,
    ontologyContraintPanelFocusOntologyNode: defaultTypeEntry,
    ontologyTemplatePanelOpened: false,
    ontologyTemplatePanelFocusOntologyNode: defaultTypeEntry,
    previouslyAnnotatedStep1JSONDoc: constants.exampleExtraction,
    previouslyAnnotatedStep1SerifXML: "",
    annotationCollection: [],
    focusTaskName: "",
    constraintAndTemplateEditorOpen: false,
  },
  getters: {
    NERConfig: (state) => {
      return state.NERConfig;
    },
    entityRelationConfig: (state) => {
      return state.entityRelationConfig;
    },
    eventConfig: (state) => {
      return state.eventConfig;
    },
    eventArgConfig: (state) => {
      return state.eventArgConfig;
    },
    stagesToRun: (state) => {
      return state.stagesToRun;
    },
    displayOntologyPanel: (state) => {
      return state.displayOntologyPanel;
    },
    focusTaskEntry: (state) => {
      return state.focusTaskEntry;
    },
    focusTaskOntologyNames: (state) => {
      return new Set(state.focusTaskEntry.ontology.map((x) => x.ontologyName));
    },
    ontologyContraintPanelOpened: (state) => {
      return state.ontologyContraintPanelOpened;
    },
    ontologyContraintPanelWorkingEntry: (state) => {
      return {
        isGlobalConstraint: state.ontologyContraintPanelFocusGlobalConstraint,
        focusOntologyNode: state.ontologyContraintPanelFocusOntologyNode,
      };
    },
    ontologyTemplateFocusNode: (state) => {
      return state.ontologyTemplatePanelFocusOntologyNode;
    },
    ontologyTemplatePanelOpened: (state) => {
      return state.ontologyTemplatePanelOpened;
    },
    originalBackendOntologyTemplate: (state) => {
      const NERConfig = _.cloneDeep(state.NERConfig);
      const entityRelationCOnfig = _.cloneDeep(state.entityRelationConfig);
      const eventConfig = _.clone(state.eventConfig);
      const eventArgConfig = _.clone(state.eventArgConfig);
      recoverOntology(NERConfig);
      recoverOntology(entityRelationCOnfig);
      recoverOntology(eventConfig);
      recoverOntology(eventArgConfig);
      return {
        stages_to_run: _.cloneDeep(state.stagesToRun),
        entity_mention: NERConfig,
        entity_mention_relation: entityRelationCOnfig,
        event_mention: eventConfig,
        event_mention_argument: eventArgConfig,
      };
    },
    previouslyAnnotatedStep1JSONDoc: (state) => {
      return state.previouslyAnnotatedStep1JSONDoc;
    },
    previouslyAnnotatedStep1SerifXML: (state) => {
      return state.previouslyAnnotatedStep1SerifXML;
    },
    annotationCollection: (state) => {
      return state.annotationCollection;
    },
    latestAnnotationCollection: (state) => {
      if (state.annotationCollection.length < 1)
        return {
          a2t_extraction: constants.exampleExtraction,
          step_1_marking_extraction: constants.exampleExtraction,
          step_1_serifxml: "",
        };
      else {
        return state.annotationCollection[
          state.annotationCollection.length - 1
        ];
      }
    },
    focusTaskName: (state) => {
      return state.focusTaskName;
    },
    constraintAndTemplateEditorOpen: (state) => {
      return state.constraintAndTemplateEditorOpen;
    },
  },
  mutations: {
    toggleDisplayOntologyPanel: (state) => {
      state.displayOntologyPanel = !state.displayOntologyPanel;
    },
    changeFocusTaskEntry: (state, payload) => {
      const focusType = payload.focusType;
      if (focusType === "NER") {
        state.focusTaskEntry = state.NERConfig;
        state.focusTaskName = "NER";
      } else if (focusType === "entityRelation") {
        state.focusTaskEntry = state.entityRelationConfig;
        state.focusTaskName = "entityRelation";
      } else if (focusType === "event") {
        state.focusTaskEntry = state.eventConfig;
        state.focusTaskName = "event";
      } else if (focusType === "eventArg") {
        state.focusTaskEntry = state.eventArgConfig;
        state.focusTaskName = "eventArg";
      } else {
        state.focusTaskEntry = defaultFocusTaskEntry;
        state.focusTaskName = "";
      }
    },
    changeTypeConfig: (state, payload) => {
      const focusNode = state.focusTaskEntry;

      const task = payload.task;
      if (task === "changeOntologyNodeName") {
        const oldName = payload.oldName;
        const newName = payload.newName;
        for (const ontologyNode of focusNode.ontology) {
          if (ontologyNode.ontologyName === oldName) {
            ontologyNode.ontologyName = newName;
          }
        }
      } else if (task === "addOntologyNode") {
        let legal = true;
        const nodeName = payload.nodeName;
        for (const ontologyNode of focusNode.ontology) {
          if (ontologyNode.ontologyName === nodeName) {
            legal = false;
            break;
          }
        }
        if (legal) {
          const newOntologyNode = _.cloneDeep(defaultTypeEntry);
          if (state.focusTaskName === "NER") {
            newOntologyNode.use_global_input_constraints = true;
          } else if (state.focusTaskName === "entityRelation") {
            newOntologyNode.use_global_input_constraints = true;
            if (nodeName !== "O") {
              newOntologyNode.input_constraints.push({
                args: {
                  allowed_mention_entity_type_pairs: [],
                },
                name: "PairMentionEntityTypeMentionEntityTypeFilter",
              });
            }
          } else if (state.focusTaskName === "event") {
            newOntologyNode.use_global_input_constraints = true;
          } else if (state.focusTaskName === "eventArg") {
            if (nodeName !== "O") {
              newOntologyNode.use_global_input_constraints = false;
              newOntologyNode.input_constraints.push({
                args: {
                  allowed_event_type_entity_type_pairs: [],
                },
                name: "EventTypeArgEntityTypeFilter",
              });
            }
          }
          focusNode.ontology.unshift(newOntologyNode);
          focusNode.ontology[0].ontologyName = nodeName;
        }
      } else if (task === "deleteOntologyNode") {
        const newOntologyNodes = [];
        const nodeName = payload.nodeName;
        for (const ontologyNode of focusNode.ontology) {
          if (ontologyNode.ontologyName !== nodeName) {
            newOntologyNodes.push(ontologyNode);
          }
        }
        focusNode.ontology = newOntologyNodes;
      }
    },
    fillOntologyConstraintPanel: (state, payload) => {
      state.ontologyContraintPanelFocusGlobalConstraint =
        payload.ontologyContraintPanelFocusGlobalConstraint;
      state.ontologyContraintPanelFocusOntologyNode =
        payload.ontologyContraintPanelFocusOntologyNode;
    },
    changeOntologyConstraintPanelStatus: (state, payload) => {
      state.ontologyContraintPanelOpened = payload.ontologyContraintPanelOpened;
    },
    changeOntologyTemplatePanelStatus: (state, payload) => {
      state.ontologyTemplatePanelOpened = payload.ontologyTemplatePanelOpened;
    },
    changeOntologyConstraintTemplatePanelStatus: (state, payload) => {
      state.constraintAndTemplateEditorOpen =
        payload.constraintAndTemplateEditorOpen;
    },
    fillOntologyTemplatePanel: (state, payload) => {
      state.ontologyTemplatePanelFocusOntologyNode =
        payload.ontologyTemplatePanelFocusOntologyNode;
    },
    importBackendOntologyConfig: (state, payload) => {
      const defaultA2TTemplate = payload.defaultA2TTemplate;
      resolveOntology(defaultA2TTemplate.entity_mention);
      resolveOntology(defaultA2TTemplate.entity_mention_relation);
      resolveOntology(defaultA2TTemplate.event_mention);
      resolveOntology(defaultA2TTemplate.event_mention_argument);
      state.NERConfig = defaultA2TTemplate.entity_mention;
      state.entityRelationConfig = defaultA2TTemplate.entity_mention_relation;
      state.eventConfig = defaultA2TTemplate.event_mention;
      state.eventArgConfig = defaultA2TTemplate.event_mention_argument;
      state.stagesToRun = defaultA2TTemplate.stages_to_run;
    },
    changeStagesToRun: (state, payload) => {
      state.stagesToRun = payload.stagesToRun;
    },
    updatePreviouslyAnnotatedStep1JSONDoc: (state, payload) => {
      state.previouslyAnnotatedStep1JSONDoc =
        payload.previouslyAnnotatedStep1JSONDoc;
    },
    updatePreviouslyAnnotatedStep1SerifXML: (state, payload) => {
      state.previouslyAnnotatedStep1SerifXML =
        payload.previouslyAnnotatedStep1SerifXML;
    },
    changeAnnotationCollection: (state, payload) => {
      const task = payload.task;
      if (task === "add") {
        state.annotationCollection.push(payload.newAnnotationEntry);
      } else if (task === "delete") {
        const index = state.annotationCollection.indexOf(
          payload.removeAnnotationEntry
        );
        if (index > -1) {
          state.annotationCollection.splice(index, 1); // 2nd parameter means remove one item only
        }
      } else if (task === "deleteByIndex") {
        state.annotationCollection.splice(payload.removeIndex, 1);
      } else if (task === "replace") {
        const index = state.annotationCollection.indexOf(
          payload.replaceAnnotationEntry
        );
        if (index > -1) {
          state.annotationCollection[index] = payload.newAnnotationEntry; // 2nd parameter means remove one item only
        }
      } else if (task === "replaceByIndex") {
        state.annotationCollection[payload.index] = payload.newAnnotationEntry;
      } else if (task === "replaceALL") {
        state.annotationCollection = payload.annotationCollection;
      } else if (task === "clear") {
        state.annotationCollection.splice(0, state.annotationCollection.length);
      }
    },
  },
  actions: {
    fetchDefaultA2TConfig: ({ commit, dispatch }, payload) => {
      commit("importBackendOntologyConfig", {
        defaultA2TTemplate: {
          entity_mention: defaultFocusTaskEntry,
          entity_mention_relation: defaultFocusTaskEntry,
          event_mention: defaultFocusTaskEntry,
          event_mention_argument: defaultFocusTaskEntry,
          stages_to_run: [],
        },
      });
      return new Promise((resolve, reject) => {
        service.getDefaultA2TTemplate().then(
          (success) => {
            const defaultA2TTemplate = success.data.default_a2t_template;
            commit("importBackendOntologyConfig", {
              defaultA2TTemplate: defaultA2TTemplate,
            });
            commit("updatePreviouslyAnnotatedStep1SerifXML", {
              previouslyAnnotatedStep1SerifXML: success.data.default_serif_doc,
            });
            commit("updatePreviouslyAnnotatedStep1JSONDoc", {
              previouslyAnnotatedStep1JSONDoc: success.data.default_extraction,
            });
            resolve();
          },
          (fail) => {
            reject(fail);
          }
        );
      });
    },
  },
  modules: {},
});
