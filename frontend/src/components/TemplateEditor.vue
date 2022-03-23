<template>
  <v-layout row justify-center>
    <v-dialog v-model="templateEditorOpen" persistent max-width="600">
      <v-card>
        <v-card-title v-text="cardTitle" />
        <v-card-text>
          <v-row v-for="(templateStr, idx1) in localTemplateArr" :key="idx1">
            <v-text-field label="Template" v-model="localTemplateArr[idx1]" />
            <v-btn icon @click="removeEnFromArr(idx1)"
              ><v-icon>mdi-minus</v-icon></v-btn
            >
          </v-row>
          <v-row
            ><v-text-field label="Template" v-model="inputBox1" /><v-btn
              icon
              @click="addNewEntryToArr()"
              ><v-icon>mdi-plus</v-icon></v-btn
            ></v-row
          >
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
export default {
  name: "TemplateEditor",
  store,
  props: [],
  data() {
    return {
      localTemplateArr: [],
      newTemplateStr: "",
      inputBox1: "",
    };
  },
  mounted() {
    this.localTemplateArr = this.copyDictStatus(
      this.$store.getters.ontologyTemplateFocusNode.templates
    );
  },
  methods: {
    copyDictStatus(oldDict) {
      return _.cloneDeep(oldDict);
    },
    closeDialog() {
      this.$store.commit("changeOntologyTemplatePanelStatus", {
        ontologyTemplatePanelOpened: false,
      });
    },
    addNewEntryToArr() {
      this.localTemplateArr.push(this.inputBox1);
      this.inputBox1 = "";
    },
    removeEnFromArr(idx) {
      this.localTemplateArr.splice(idx, 1);
    },
    saveChanges() {
      this.$store.getters.ontologyTemplateFocusNode.templates =
        this.localTemplateArr;
      this.closeDialog();
    },
  },
  computed: {
    templateEditorOpen() {
      return this.$store.getters.ontologyTemplatePanelOpened;
    },
    focusTaskEntry() {
      return this.$store.getters.focusTaskEntry;
    },
    focusTaskNode() {
      return this.$store.getters.ontologyTemplateFocusNode;
    },
    cardTitle() {
      return this.focusTaskNode.ontologyName + " templates";
    },
  },
};
</script>
