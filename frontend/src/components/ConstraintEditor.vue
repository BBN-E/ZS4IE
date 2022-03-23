<template>
  <v-layout row justify-center>
    <v-dialog v-model="constraintEditorOpen" persistent max-width="600">
      <v-card>
        <v-card-title v-text="cardTitle"></v-card-title>
        <v-card-text>
          <v-col>
            <v-switch
              label="Apply global constraints"
              v-if="!isGlobalConstraint"
              v-model="localUseGlobalConstraints"
            ></v-switch>
            <v-card v-for="(constraint, idx) in localConstraintArr" :key="idx">
              <v-card-title
                >{{ constraint.name }}<v-spacer /><v-btn
                  icon
                  @click="removeEnFromArr(localConstraintArr, idx)"
                  ><v-icon>mdi-minus</v-icon></v-btn
                ></v-card-title
              >
              <v-card-text v-if="constraint.name === 'MentionTypeFilter'">
                <v-switch
                  label="name"
                  v-model="constraint.args.allowed_mention_types"
                  value="name"
                ></v-switch
                ><v-switch
                  label="pron"
                  v-model="constraint.args.allowed_mention_types"
                  value="pron"
                ></v-switch
                ><v-switch
                  label="desc"
                  v-model="constraint.args.allowed_mention_types"
                  value="desc"
                ></v-switch>
              </v-card-text>
              <v-card-text
                v-if="
                  constraint.name ===
                  'PairMentionEntityTypeMentionEntityTypeFilter'
                "
              >
                <v-row
                  v-for="(allowedMentionEntityTypePair, idx2) in constraint.args
                    .allowed_mention_entity_type_pairs"
                  :key="idx2"
                >
                  <v-text-field
                    label="LeftEntityType"
                    v-model="allowedMentionEntityTypePair[0]"
                  /><v-text-field
                    label="RightEntityType"
                    v-model="allowedMentionEntityTypePair[1]"
                  />
                  <v-btn
                    icon
                    @click="
                      removeEnFromArr(
                        constraint.args.allowed_mention_entity_type_pairs,
                        idx2
                      )
                    "
                    ><v-icon>mdi-minus</v-icon></v-btn
                  >
                </v-row>
                <v-row>
                  <v-text-field
                    label="LeftEntityType"
                    v-model="inputBox1"
                  /><v-text-field
                    label="RightEntityType"
                    v-model="inputBox2"
                  /><v-btn
                    icon
                    @click="
                      addNewEntryToArr(
                        2,
                        constraint.args.allowed_mention_entity_type_pairs
                      )
                    "
                    ><v-icon>mdi-plus</v-icon></v-btn
                  >
                </v-row>
              </v-card-text>
              <v-card-text v-if="constraint.name === 'PairMentionModelFilter'">
                <v-row
                  v-for="(allowModelName, idx2) in constraint.args
                    .allowed_model_names"
                  :key="idx2"
                >
                  <v-text-field
                    label="ModelName"
                    v-model="constraint.args.allowed_model_names[idx2]"
                  />
                  <v-btn
                    icon
                    @click="
                      removeEnFromArr(constraint.args.allowed_model_names, idx2)
                    "
                    ><v-icon>mdi-minus</v-icon></v-btn
                  >
                </v-row>
                <v-row>
                  <v-text-field label="ModelName" v-model="inputBox1" />
                  <v-btn
                    icon
                    @click="
                      addNewEntryToArr(1, constraint.args.allowed_model_names)
                    "
                    ><v-icon>mdi-plus</v-icon></v-btn
                  >
                </v-row>
              </v-card-text>
              <v-card-text
                v-if="constraint.name === 'EventTypeArgEntityTypeFilter'"
              >
                <v-row
                  v-for="(allowedEventTypeEntityTypePair, idx2) in constraint
                    .args.allowed_event_type_entity_type_pairs"
                  :key="idx2"
                >
                  <v-text-field
                    label="LeftEventType"
                    v-model="allowedEventTypeEntityTypePair[0]"
                  /><v-text-field
                    label="RightEntityType"
                    v-model="allowedEventTypeEntityTypePair[1]"
                  />
                  ><v-btn
                    icon
                    @click="
                      removeEnFromArr(
                        constraint.args.allowed_event_type_entity_type_pairs,
                        idx2
                      )
                    "
                    ><v-icon>mdi-minus</v-icon></v-btn
                  >
                </v-row>
                <v-row>
                  <v-text-field
                    label="LeftEventType"
                    v-model="inputBox1"
                  /><v-text-field
                    label="RightEntityType"
                    v-model="inputBox2"
                  /><v-btn
                    icon
                    @click="
                      addNewEntryToArr(
                        2,
                        constraint.args.allowed_event_type_entity_type_pairs
                      )
                    "
                    ><v-icon>mdi-plus</v-icon></v-btn
                  >
                </v-row>
              </v-card-text>
              <v-card-text> </v-card-text>
            </v-card>
            <v-card>
              <v-card-text>
                <v-row>
                  <v-select
                    :items="totalConstraintSet"
                    label="Constraint Name"
                    v-model="addNewConstraintName"
                  ></v-select>
                  <v-btn icon @click="addNewConstrint()"
                    ><v-icon>mdi-plus</v-icon></v-btn
                  >
                </v-row>
              </v-card-text>
            </v-card>
          </v-col>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn color="primary" @click="saveChanges()"> Save </v-btn>
          <v-btn @click="closeDialog()">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-layout>
</template>

<script>
import store from "@/store/index.js";
import _ from "lodash";
const totalConstraintSet = [
  "MentionTypeFilter",
  "PairMentionEntityTypeMentionEntityTypeFilter",
  "PairMentionModelFilter",
  "EventTypeArgEntityTypeFilter",
];
export default {
  name: "ConstraintEditor",
  store,
  props: [],
  data() {
    return {
      localConstraintArr: [],
      localUseGlobalConstraints: false,
      inputBox1: "",
      inputBox2: "",
      pendingAddingNewConstraint: "",
      totalConstraintSet: totalConstraintSet,
      addNewConstraintName: "",
    };
  },
  mounted() {
    this.localConstraintArr = [];
    const en = this.$store.getters.ontologyContraintPanelWorkingEntry;
    if (en.isGlobalConstraint) {
      for (const constraint of this.$store.getters.focusTaskEntry
        .input_constraints) {
        this.localConstraintArr.push(this.copyDictStatus(constraint));
      }
      this.localUseGlobalConstraints = false;
    } else {
      for (const constraint of en.focusOntologyNode.input_constraints) {
        this.localConstraintArr.push(this.copyDictStatus(constraint));
      }
      this.localUseGlobalConstraints =
        en.focusOntologyNode.use_global_input_constraints || false;
    }
  },
  methods: {
    copyDictStatus(oldDict) {
      return _.cloneDeep(oldDict);
    },
    closeDialog() {
      this.$store.commit("changeOntologyConstraintPanelStatus", {
        ontologyContraintPanelOpened: false,
      });
    },
    addNewEntryToArr(elemToAdd, arrToAdd) {
      if (elemToAdd === 1) {
        arrToAdd.push(this.inputBox1);
      } else if (elemToAdd === 2) {
        arrToAdd.push([this.inputBox1, this.inputBox2]);
      }
      this.inputBox1 = "";
      this.inputBox2 = "";
    },
    removeEnFromArr(arrToRemove, idx) {
      arrToRemove.splice(idx, 1);
    },
    addNewConstrint() {
      const newConstraintName = this.addNewConstraintName;
      if (newConstraintName === "MentionTypeFilter") {
        this.localConstraintArr.push({
          name: newConstraintName,
          args: {
            allowed_mention_types: [],
          },
        });
      } else if (
        newConstraintName === "PairMentionEntityTypeMentionEntityTypeFilter"
      ) {
        this.localConstraintArr.push({
          name: newConstraintName,
          args: {
            allowed_mention_entity_type_pairs: [],
          },
        });
      } else if (newConstraintName === "PairMentionModelFilter") {
        this.localConstraintArr.push({
          name: newConstraintName,
          args: {
            allowed_model_names: [],
          },
        });
      } else if (newConstraintName === "EventTypeArgEntityTypeFilter") {
        this.localConstraintArr.push({
          name: newConstraintName,
          args: {
            allowed_event_type_entity_type_pairs: [],
          },
        });
      }
    },
    saveChanges() {
      const en = this.$store.getters.ontologyContraintPanelWorkingEntry;
      if (en.isGlobalConstraint) {
        this.$store.getters.focusTaskEntry.input_constraints =
          this.localConstraintArr;
      } else {
        en.focusOntologyNode.input_constraints = this.localConstraintArr;
        en.focusOntologyNode.use_global_input_constraints =
          this.localUseGlobalConstraints;
      }
      this.closeDialog();
    },
  },
  computed: {
    constraintEditorOpen() {
      return this.$store.getters.ontologyContraintPanelOpened;
    },
    focusTaskEntry() {
      return this.$store.getters.focusTaskEntry;
    },
    isGlobalConstraint() {
      return this.$store.getters.ontologyContraintPanelWorkingEntry
        .isGlobalConstraint;
    },

    cardTitle() {
      const en = this.$store.getters.ontologyContraintPanelWorkingEntry;
      if (en.isGlobalConstraint) {
        return "Global Constraint";
      } else {
        return en.focusOntologyNode.ontologyName + " Constraint";
      }
    },
  },
};
</script>
