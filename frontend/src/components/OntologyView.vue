<template>
  <v-container fluid>
    <v-card>
      <v-card-title>Template Curation</v-card-title>
      <v-card-text>
        <v-card elevation="0">
          <v-card-text>
            <v-tabs v-model="tab" align-with-title>
              <v-tabs-slider color="yellow"></v-tabs-slider>

              <v-tab v-for="item in items" :key="item">
                {{ item }}
              </v-tab>
            </v-tabs>
            <v-tabs-items v-model="tab">
              <v-tab-item v-for="item in items" :key="item">
                <v-card class="d-inline-flex flex-wrap">
                  <!-- <v-card class="fix-width-card" outlined>
                    <v-card-title
                      >Global constraints<v-spacer />
                      <v-btn @click="editConstraint(true, null)" icon
                        ><v-icon>mdi-pencil-outline</v-icon></v-btn
                      ></v-card-title
                    >
                    <v-card-text>
                      <ConstraintBoard
                        :input_constraints="focusTaskEntry.input_constraints"
                        :taskName="item"
                        :ontologyName="null"
                        :isGlobalConstraint="true"
                        :use_global_input_constraints="false"
                      />
                    </v-card-text>
                  </v-card> -->
                  <v-card
                    class="d-flex justify-center align-center align-content-center fix-width-card"
                    outlined
                  >
                    <v-btn @click="popUpAddTypeDialog(item)" icon
                      ><v-icon>mdi-plus</v-icon></v-btn
                    >
                  </v-card>
                  <v-card
                    v-for="ontology in focusTaskEntry.ontology"
                    :key="ontology.ontologyName"
                    class="fix-width-card"
                    outlined
                  >
                    <v-card-title
                      >{{ ontology.ontologyName }}<v-spacer />
                      <v-btn icon @click="editOntologyNodeNew(ontology)"
                        ><v-icon> mdi-pencil-outline </v-icon></v-btn
                      >
                      <v-btn
                        icon
                        @click="
                          removeCurrentOntologyType(ontology.ontologyName)
                        "
                        ><v-icon>mdi-minus</v-icon></v-btn
                      ></v-card-title
                    >
                    <v-card-text>
                      <div
                        elevation="0"
                        v-if="item === 'Relation' || item === 'Event Argument'"
                      >
                        <ConstraintBoard
                          :input_constraints="ontology.input_constraints"
                          :taskName="item"
                          :ontologyName="ontology.ontologyName"
                          :isGlobalConstraint="false"
                          :use_global_input_constraints="
                            ontology.use_global_input_constraints
                          "
                        />
                      </div>
                      <div>
                        <v-card>
                          <v-card-text>
                            <p
                              v-for="(template, idx2) in ontology.templates"
                              :key="idx2"
                              v-text="template"
                            ></p>
                          </v-card-text>
                        </v-card>
                      </div>
                    </v-card-text>
                  </v-card>
                </v-card>
              </v-tab-item>
            </v-tabs-items>
          </v-card-text>
        </v-card>
        <v-card elevation="0">
          <v-card-text>
            <v-row>
              <v-file-input
                v-model="selectedLocalConfigFile"
                label="Template file path"
              ></v-file-input>
              <v-btn @click="loadConfig()">Load Templates</v-btn>
              <v-btn @click="saveConfig()">Save Templates</v-btn>
            </v-row>
          </v-card-text>
        </v-card>
      </v-card-text>
    </v-card>

    <v-dialog v-model="addTypeDialogOpen">
      <v-card>
        <v-card-title class="text-h5 grey lighten-2">
          Add new type under {{ addTypeParentClass }}
        </v-card-title>

        <v-card-text>
          <v-col>
            <v-text-field
              label="New Type Name"
              v-model="addTypeNewTypeName"
              clearable
              @focus="clearAddTypeValidation()"
            />
            <v-btn text @click="verifyAddTypeName()">Verify</v-btn>
          </v-col>
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            text
            @click="addTypeExec()"
            :disabled="!addTypeFormValid"
          >
            Add
          </v-btn>
          <v-btn color="error" text @click="addTypeDialogOpen = false">
            Cancel</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
    <ConstraintEditor v-if="constraintEditorOpen" />
    <TemplateEditor v-if="templateEditorOpen" />
    <ConstraintTemplateEditor v-if="constraintTemplateEditorOpen" />
  </v-container>
</template>
<script>
import store from "@/store/index.js";
import ConstraintEditor from "@/components/ConstraintEditor.vue";
import TemplateEditor from "@/components/TemplateEditor.vue";
import ConstraintBoard from "@/components/ConstraintBoard.vue";
import ConstraintTemplateEditor from "@/components/ConstraintTemplateEditor.vue";
export default {
  name: "OntologyView",
  store,
  data() {
    return {
      tab: 0,
      items: ["Entity", "Relation", "Event", "Event Argument"],
      dummyFocusEntry: {
        ontologyName: "",
      },
      addTypeDialogOpen: false,
      addTypeParentClass: "",
      addTypeNewTypeName: "",
      addTypeFormValid: false,
      addTypeErrorMsg: "",
      selectedLocalConfigFile: null,
    };
  },
  mounted() {},
  computed: {
    focusCurrentOntologyNames() {
      return this.$store.getters.focusTaskOntologyNames;
    },
    focusTaskEntry() {
      return this.$store.getters.focusTaskEntry;
    },
    constraintEditorOpen() {
      return this.$store.getters.ontologyContraintPanelOpened;
    },
    templateEditorOpen() {
      return this.$store.getters.ontologyTemplatePanelOpened;
    },
    constraintTemplateEditorOpen() {
      return this.$store.getters.constraintAndTemplateEditorOpen;
    },
  },
  methods: {
    popUpAddTypeDialog(parentOntologyType) {
      this.addTypeParentClass = parentOntologyType;
      this.addTypeDialogOpen = true;
      this.addTypeNewTypeName = "";
    },
    addTypeExec() {
      this.$store.commit("changeTypeConfig", {
        task: "addOntologyNode",
        nodeName: this.addTypeNewTypeName,
      });
      this.addTypeDialogOpen = false;
    },
    verifyAddTypeName() {
      if (
        !this.focusCurrentOntologyNames.has(this.addTypeNewTypeName) &&
        this.addTypeNewTypeName.length > 0
      ) {
        this.addTypeFormValid = true;
        this.addTypeErrorMsg = "";
      } else {
        this.addTypeFormValid = false;
        this.addTypeErrorMsg =
          this.addTypeNewTypeName.length > 0
            ? "Need non-empty type"
            : "Duplicated type name";
      }
    },
    clearAddTypeValidation() {
      this.addTypeFormValid = false;
      this.addTypeErrorMsg = "";
    },
    editConstraint(isGlobalConstraint, focusOntologyNode) {
      this.$store.commit("fillOntologyConstraintPanel", {
        ontologyContraintPanelFocusGlobalConstraint: isGlobalConstraint,
        ontologyContraintPanelFocusOntologyNode: focusOntologyNode,
      });
      this.$store.commit("changeOntologyConstraintPanelStatus", {
        ontologyContraintPanelOpened: true,
      });
    },
    editTemplate(focusOntologyNode) {
      this.$store.commit("fillOntologyTemplatePanel", {
        ontologyTemplatePanelFocusOntologyNode: focusOntologyNode,
      });
      this.$store.commit("changeOntologyTemplatePanelStatus", {
        ontologyTemplatePanelOpened: true,
      });
    },
    removeCurrentOntologyType(ontologyTypeName) {
      this.$store.commit("changeTypeConfig", {
        task: "deleteOntologyNode",
        nodeName: ontologyTypeName,
      });
    },
    loadConfig() {
      const reader = new FileReader();
      reader.onload = (event) => {
        const jsonStr = event.target.result;
        const A2TFullConfig = JSON.parse(jsonStr);
        this.$store.commit("importBackendOntologyConfig", {
          defaultA2TTemplate: A2TFullConfig,
        });
        this.$store.commit("changeFocusTaskEntry", {
          focusType: "NER",
        });
      };
      reader.readAsText(this.selectedLocalConfigFile);
    },
    saveConfig() {
      const A2TParsingRet = this.$store.getters.originalBackendOntologyTemplate;
      const a = document.createElement("a");
      a.href = URL.createObjectURL(
        new Blob([JSON.stringify(A2TParsingRet, null, 2)], {
          type: "text/plain",
        })
      );
      a.setAttribute("download", "a2t_template.json");
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    },
    editOntologyNodeNew(ontologyNode) {
      this.$store.commit("fillOntologyConstraintPanel", {
        ontologyContraintPanelFocusGlobalConstraint: false,
        ontologyContraintPanelFocusOntologyNode: ontologyNode,
      });
      this.$store.commit("changeOntologyConstraintTemplatePanelStatus", {
        constraintAndTemplateEditorOpen: true,
      });
    },
  },
  components: {
    ConstraintEditor,
    TemplateEditor,
    ConstraintBoard,
    ConstraintTemplateEditor,
  },
  watch: {
    tab(newVal, oldVal) {
      if (newVal !== null) {
        if (this.items[this.tab] === "Entity") {
          this.$store.commit("changeFocusTaskEntry", {
            focusType: "NER",
          });
        } else if (this.items[this.tab] === "Relation") {
          this.$store.commit("changeFocusTaskEntry", {
            focusType: "entityRelation",
          });
        } else if (this.items[this.tab] === "Event") {
          this.$store.commit("changeFocusTaskEntry", {
            focusType: "event",
          });
        } else if (this.items[this.tab] === "Event Argument") {
          this.$store.commit("changeFocusTaskEntry", {
            focusType: "eventArg",
          });
        }
      }
    },
  },
};
</script>
<style scope>
.fix-width-card {
  width: 340px;
}
</style>
