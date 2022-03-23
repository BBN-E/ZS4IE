<template>
  <v-container fluid>
    <v-snackbar v-model="snackbarSwitch" :timeout="-1">
      {{ snackbarMsg }}

      <template v-slot:action="{ attrs }">
        <v-btn color="pink" text v-bind="attrs" @click="snackbarSwitch = false">
          Close
        </v-btn>
      </template>
    </v-snackbar>
    <v-card>
      <v-card-title>Output</v-card-title>
      <v-card-text>
        <v-col v-if="annotationCollection.length > 0">
          <v-row>
            <v-col>
              <v-pagination
                v-model="currentAnnotationIdxPlusOne"
                :length="annotationCollection.length"
              ></v-pagination>
            </v-col>
          </v-row>
          <v-row
            ><v-switch
              label="Selected for inference"
              v-model="
                annotationCollection[currentAnnotationIdxPlusOne - 1]
                  .select_for_scoring
              "
            />
            <v-spacer />
            <v-btn
              icon
              @click="removeDocAnnotation(currentAnnotationIdxPlusOne - 1)"
              ><v-icon>mdi-minus</v-icon></v-btn
            >
          </v-row>
          <v-row
            v-for="(taskName, idx) in annotationTaskOrderComputed"
            :key="idx"
          >
            <v-col>
              <v-card>
                <v-card-title>{{
                  ProgrammingTaskNameToUITaskName[taskName]
                }}</v-card-title>
                <v-card-text>
                  <UnarySpanAdjudicator
                    task="NER"
                    :annotationCollectionIdx="currentAnnotationIdxPlusOne - 1"
                    v-if="taskName === 'NER'"
                  />
                  <BinarySpanAdjudicator
                    task="Relation"
                    :annotationCollectionIdx="currentAnnotationIdxPlusOne - 1"
                    v-if="taskName === 'Relation'"
                  />
                  <UnarySpanAdjudicator
                    task="EventMention"
                    :annotationCollectionIdx="currentAnnotationIdxPlusOne - 1"
                    v-if="taskName === 'EventMention'"
                  />
                  <BinarySpanAdjudicator
                    task="EventArgument"
                    :annotationCollectionIdx="currentAnnotationIdxPlusOne - 1"
                    v-if="taskName === 'EventArgument'"
                  />
                </v-card-text>
              </v-card>
            </v-col>
            <v-col>
              <v-card class="stickBoard">
                <v-card-title
                  >{{
                    ProgrammingTaskNameToUITaskName[taskName]
                  }}
                  Score</v-card-title
                >
                <v-card-text>
                  <ScoringBoard v-if="taskName === 'NER'" task="NER" />
                  <ScoringBoard
                    v-if="taskName === 'Relation'"
                    task="Relation"
                  />
                  <ScoringBoard
                    v-if="taskName === 'EventMention'"
                    task="EventMention"
                  />
                  <ScoringBoard
                    v-if="taskName === 'EventArgument'"
                    task="EventArgument"
                  />
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-col>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
import store from "@/store/index.js";
import UnarySpanAdjudicator from "@/components/UnarySpanAdjudicator.vue";
import BinarySpanAdjudicator from "@/components/BinarySpanAdjudicator.vue";
import ScoringBoard from "@/components/ScoringBoard.vue";
import service from "@/service/main";
const ProgrammingTaskNameToUITaskName = {
  NER: "NER",
  Relation: "Relation extraction",
  EventMention: "Event extraction",
  EventArgument: "Event argument extraction",
};
export default {
  name: "AdjudicationBoard",
  store,
  data() {
    return {
      currentAnnotationIdxPlusOne: 1,
      snackbarSwitch: false,
      snackbarMsg: "",
      annotationTaskOrder: ["NER", "Relation", "EventMention", "EventArgument"],
    };
  },
  methods: {
    removeDocAnnotation(index) {
      this.$store.commit("changeAnnotationCollection", {
        task: "deleteByIndex",
        removeIndex: index,
      });
    },
    calculateStatusticsForDoc(collectionIdx) {
      const ret = {
        entityAnnotated: 0,
        entityGood: 0,
        entityBad: 0,
        entityRelationAnnotated: 0,
        entityRelationGood: 0,
        entityRelationBad: 0,
        eventAnnotated: 0,
        eventGood: 0,
        eventBad: 0,
        eventArgAnnotated: 0,
        eventArgGood: 0,
        eventArgBad: 0,
      };
      if (
        this.annotationCollection.length === 0 ||
        collectionIdx < 0 ||
        collectionIdx >= this.annotationCollection.length
      )
        return ret;
      const focusDoc = this.annotationCollection[collectionIdx].a2t_extraction;
      for (const sentence of focusDoc.sentences) {
        for (const mention of sentence.mentions) {
          if (mention.is_frozen) {
            ret.entityAnnotated++;
            if (mention.is_good) {
              ret.entityGood++;
            } else {
              ret.entityBad++;
            }
          }
        }
        for (const eventMention of sentence.event_mentions) {
          if (eventMention.is_frozen) {
            ret.eventAnnotated++;
            if (eventMention.is_good) {
              ret.eventGood++;
            } else {
              ret.eventBad++;
            }
          }
          for (const eventArg of eventMention.event_args) {
            if (eventArg.is_frozen) {
              ret.eventArgAnnotated++;
              if (eventArg.is_good) {
                ret.eventArgGood++;
              } else {
                ret.eventArgBad++;
              }
            }
          }
        }
      }
      for (const entityRelation of focusDoc.entity_relations) {
        if (entityRelation.is_frozen) {
          ret.entityRelationAnnotated++;
          if (entityRelation.is_good) {
            ret.entityRelationGood++;
          } else {
            ret.entityRelationBad++;
          }
        }
      }
      return ret;
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

    annotationTaskOrderComputed() {
      const ret = [];
      const vuexOntologyNameToLocalOntologyName = {
        "": "",
        NER: "NER",
        entityRelation: "Relation",
        event: "EventMention",
        eventArg: "EventArgument",
      };
      const focusTaskName =
        vuexOntologyNameToLocalOntologyName[this.$store.getters.focusTaskName];
      if (focusTaskName.length > 0) {
        ret.push(focusTaskName);
      }
      for (const taskName of this.annotationTaskOrder) {
        if (!ret.includes(taskName)) {
          ret.push(taskName);
        }
      }
      return ret;
    },
    ProgrammingTaskNameToUITaskName() {
      return ProgrammingTaskNameToUITaskName;
    },
  },
  components: {
    UnarySpanAdjudicator,
    BinarySpanAdjudicator,
    ScoringBoard,
  },
};
</script>

<style scope>
.stickBoard {
  position: -webkit-sticky;
  position: sticky;
  top: 80px;
}
</style>
