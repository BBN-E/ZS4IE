<template>
  <v-card>
    <v-card-title>Inference configuration</v-card-title>
    <v-snackbar v-model="snackbarSwitch" :timeout="-1">
      {{ snackbarMsg }}

      <template v-slot:action="{ attrs }">
        <v-btn color="pink" text v-bind="attrs" @click="snackbarSwitch = false">
          Close
        </v-btn>
      </template>
    </v-snackbar>
    <v-card-text>
      <v-col>
        <v-row>
          <v-card style="width: 100%" elevation="0">
            <v-card-text>
              <v-row>
                <v-switch
                  label="NER"
                  v-model="stagesToRun"
                  value="entity_mention"
                ></v-switch>
                <v-spacer />
                <v-switch
                  label="Relation extraction"
                  v-model="stagesToRun"
                  value="entity_mention_relation"
                ></v-switch>
                <v-spacer />
                <v-switch
                  label="Event extraction"
                  v-model="stagesToRun"
                  value="event_mention"
                ></v-switch>
                <v-spacer />
                <v-switch
                  label="Event argument extration"
                  v-model="stagesToRun"
                  value="event_mention_argument"
                ></v-switch>
              </v-row>
              <v-row
                ><v-spacer /><v-btn @click="rescore()"
                  >Run Inference</v-btn
                ></v-row
              >
            </v-card-text>
          </v-card>
        </v-row>
        <v-row>
          <v-card style="width: 100%" elevation="0">
            <v-card-title> </v-card-title>
            <v-card-text>
              <v-row>
                <v-file-input
                  v-model="selectedLocalAnnotatedFile"
                  label="Annotated file path"
                ></v-file-input>
                <v-btn @click="loadAnnotation()">Load Annotation</v-btn>
                <v-btn @click="saveAnnotation()">Save Annotation</v-btn>
              </v-row>
            </v-card-text>
          </v-card>
        </v-row>
      </v-col>
    </v-card-text>
  </v-card>
</template>

<script>
import service from "@/service/main";
import store from "@/store/index.js";
export default {
  name: "InferenceConfig",
  store,
  data() {
    return {
      snackbarSwitch: false,
      snackbarMsg: "",
      selectedLocalAnnotatedFile: null,
    };
  },
  methods: {
    rescoreDocByIndex(currentIdx, totalList) {
      service
        .scoreDocument(
          this.annotationCollection[currentIdx],
          this.$store.getters.originalBackendOntologyTemplate
        )
        .then(
          (success) => {
            this.refreshMsg(currentIdx, totalList);
            this.annotationCollection[currentIdx].a2t_extraction =
              success.data.extraction;
          },
          (fail) => {
            console.log(fail);
            this.refreshMsg(currentIdx, totalList);
          }
        );
    },
    rescore() {
      const pendingScoreIdxs = [];
      for (let i = 0; i < this.annotationCollection.length; i++) {
        const annotationEntry = this.annotationCollection[i];
        if (annotationEntry.select_for_scoring) {
          pendingScoreIdxs.push(i);
        }
      }
      this.showSnackBarMessage("Scoring " + pendingScoreIdxs.length + " docs");
      for (const rescoreIdx of pendingScoreIdxs) {
        this.rescoreDocByIndex(rescoreIdx, pendingScoreIdxs);
      }
    },
    showSnackBarMessage(message) {
      this.snackbarMsg = message;
      this.snackbarSwitch = true;
    },
    hideSnackBar() {
      this.snackbarSwitch = false;
    },
    refreshMsg(finishedIdx, totalList) {
      const index = totalList.indexOf(finishedIdx);
      if (index > -1) {
        totalList.splice(index, 1); // 2nd parameter means remove one item only
      }
      if (totalList.length > 0) {
        this.showSnackBarMessage("Scoring " + totalList.length + " docs");
      } else {
        this.hideSnackBar();
      }
    },
    loadAnnotation() {
      const reader = new FileReader();
      reader.onload = (event) => {
        const jsonStr = event.target.result;
        const annotationJSON = JSON.parse(jsonStr);
        this.$store.commit("changeAnnotationCollection", {
          task: "replaceALL",
          annotationCollection: annotationJSON,
        });
      };
      reader.readAsText(this.selectedLocalAnnotatedFile);
    },
    saveAnnotation() {
      const annotationCollection = this.$store.getters.annotationCollection;
      const a = document.createElement("a");
      a.href = URL.createObjectURL(
        new Blob([JSON.stringify(annotationCollection, null, 2)], {
          type: "text/plain",
        })
      );
      a.setAttribute("download", "annotation_collection.json");
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    },
  },
  computed: {
    annotationCollection() {
      return this.$store.getters.annotationCollection;
    },
    statisticsForCurrentDoc() {
      return this.calculateStatusticsForDoc(
        this.currentAnnotationIdxPlusOne - 1
      );
    },
    stagesToRun: {
      get() {
        return this.$store.getters.stagesToRun;
      },
      set(newValue) {
        this.$store.commit("changeStagesToRun", { stagesToRun: newValue });
      },
    },
  },
};
</script>
