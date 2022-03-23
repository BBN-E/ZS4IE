<template>
  <v-card elevation="0">
    <v-card-text>
      <v-card elevation="0">
        <v-card-text>
          <v-data-table
            :headers="taskTable.headers"
            :items="taskTable.items"
          ></v-data-table>
        </v-card-text>
      </v-card>
      <v-card elevation="0">
        <v-card-text>
          <v-data-table
            :headers="typeTable.headers"
            :items="typeTable.items"
          ></v-data-table>
        </v-card-text>
      </v-card>
      <v-card elevation="0">
        <v-card-text>
          <v-data-table
            :headers="templateTable.headers"
            :items="templateTable.items"
          ></v-data-table>
        </v-card-text>
      </v-card>
    </v-card-text>
  </v-card>
</template>

<script>
import store from "@/store/index.js";
export default {
  name: "ScoringBoard",
  store,
  data() {
    return {};
  },
  methods: {},
  mounted() {},
  computed: {
    annotationStatistics() {
      const ret = {
        taskStatistics: { total: 0, good: 0, bad: 0 },
        typeStatistics: {},
        templateStatistics: {},
      };
      for (const annotatedDoc of this.$store.getters.annotationCollection) {
        const a2tExtraction = annotatedDoc.a2t_extraction;
        if (this.task === "Relation") {
          for (const entityRelation of a2tExtraction.entity_relations) {
            if (
              entityRelation.is_frozen &&
              entityRelation.model === "Ask2Transformers"
            ) {
              const isGood = entityRelation.is_good;
              const relationType = entityRelation.rel_type;
              // Task level
              ret.taskStatistics.total++;
              if (isGood) {
                ret.taskStatistics.good++;
              } else {
                ret.taskStatistics.bad++;
              }
              // Type Level
              if (!(relationType in ret.typeStatistics)) {
                ret.typeStatistics[relationType] = {
                  total: 0,
                  good: 0,
                  bad: 0,
                };
              }
              ret.typeStatistics[relationType].total++;
              if (isGood) {
                ret.typeStatistics[relationType].good++;
              } else {
                ret.typeStatistics[relationType].bad++;
              }
              // templateLevel
              const patterns = JSON.parse(entityRelation.pattern);
              for (const pattern of patterns) {
                const patternStr = pattern[1];
                if (!(patternStr in ret.templateStatistics)) {
                  ret.templateStatistics[patternStr] = {
                    total: 0,
                    good: 0,
                    bad: 0,
                  };
                }
                ret.templateStatistics[patternStr].total++;
                if (isGood) {
                  ret.templateStatistics[patternStr].good++;
                } else {
                  ret.templateStatistics[patternStr].bad++;
                }
              }
            }
          }
        } else {
          for (const sentence of a2tExtraction.sentences) {
            if (this.task === "NER") {
              for (const mention of sentence.mentions) {
                if (mention.is_frozen && mention.model === "Ask2Transformers") {
                  const isGood = mention.is_good;
                  const entityType = mention.entity_type;
                  // Task level
                  ret.taskStatistics.total++;
                  if (isGood) {
                    ret.taskStatistics.good++;
                  } else {
                    ret.taskStatistics.bad++;
                  }
                  // Type Level
                  if (!(entityType in ret.typeStatistics)) {
                    ret.typeStatistics[entityType] = {
                      total: 0,
                      good: 0,
                      bad: 0,
                    };
                  }
                  ret.typeStatistics[entityType].total++;
                  if (isGood) {
                    ret.typeStatistics[entityType].good++;
                  } else {
                    ret.typeStatistics[entityType].bad++;
                  }
                  // templateLevel
                  const patterns = JSON.parse(mention.pattern);
                  for (const pattern of patterns) {
                    const patternStr = pattern[1];
                    if (!(patternStr in ret.templateStatistics)) {
                      ret.templateStatistics[patternStr] = {
                        total: 0,
                        good: 0,
                        bad: 0,
                      };
                    }
                    ret.templateStatistics[patternStr].total++;
                    if (isGood) {
                      ret.templateStatistics[patternStr].good++;
                    } else {
                      ret.templateStatistics[patternStr].bad++;
                    }
                  }
                }
              }
            } else if (
              this.task === "EventMention" ||
              this.task === "EventArgument"
            ) {
              for (const eventMention of sentence.event_mentions) {
                if (this.task === "EventMention") {
                  if (
                    eventMention.is_frozen &&
                    eventMention.model === "Ask2Transformers"
                  ) {
                    const isGood = eventMention.is_good;
                    const eventType = eventMention.event_type;
                    // Task level
                    ret.taskStatistics.total++;
                    if (isGood) {
                      ret.taskStatistics.good++;
                    } else {
                      ret.taskStatistics.bad++;
                    }
                    // Type Level
                    if (!(eventType in ret.typeStatistics)) {
                      ret.typeStatistics[eventType] = {
                        total: 0,
                        good: 0,
                        bad: 0,
                      };
                    }
                    ret.typeStatistics[eventType].total++;
                    if (isGood) {
                      ret.typeStatistics[eventType].good++;
                    } else {
                      ret.typeStatistics[eventType].bad++;
                    }
                    // templateLevel
                    const patterns = JSON.parse(eventMention.pattern_id);
                    for (const pattern of patterns) {
                      const patternStr = pattern[1];
                      if (!(patternStr in ret.templateStatistics)) {
                        ret.templateStatistics[patternStr] = {
                          total: 0,
                          good: 0,
                          bad: 0,
                        };
                      }
                      ret.templateStatistics[patternStr].total++;
                      if (isGood) {
                        ret.templateStatistics[patternStr].good++;
                      } else {
                        ret.templateStatistics[patternStr].bad++;
                      }
                    }
                  }
                } else if (this.task === "EventArgument") {
                  for (const eventArg of eventMention.event_args) {
                    if (
                      eventArg.is_frozen &&
                      eventArg.model === "Ask2Transformers"
                    ) {
                      const isGood = eventArg.is_good;
                      const eventArgrole = eventArg.role;
                      // Task level
                      ret.taskStatistics.total++;
                      if (isGood) {
                        ret.taskStatistics.good++;
                      } else {
                        ret.taskStatistics.bad++;
                      }
                      // Type Level
                      if (!(eventArgrole in ret.typeStatistics)) {
                        ret.typeStatistics[eventArgrole] = {
                          total: 0,
                          good: 0,
                          bad: 0,
                        };
                      }
                      ret.typeStatistics[eventArgrole].total++;
                      if (isGood) {
                        ret.typeStatistics[eventArgrole].good++;
                      } else {
                        ret.typeStatistics[eventArgrole].bad++;
                      }
                      // templateLevel
                      const patterns = JSON.parse(eventArg.pattern);
                      for (const pattern of patterns) {
                        const patternStr = pattern[1];
                        if (!(patternStr in ret.templateStatistics)) {
                          ret.templateStatistics[patternStr] = {
                            total: 0,
                            good: 0,
                            bad: 0,
                          };
                        }
                        ret.templateStatistics[patternStr].total++;
                        if (isGood) {
                          ret.templateStatistics[patternStr].good++;
                        } else {
                          ret.templateStatistics[patternStr].bad++;
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }

      return ret;
    },
    taskTable() {
      const headers = [
        {
          text: "Task",
          value: "Task",
        },
        { text: "Total", value: "total" },
        { text: "Correct", value: "goodMarked" },
        { text: "Incorrect", value: "badMarked" },
      ];
      const items = [
        {
          Task: this.task,
          total: this.annotationStatistics.taskStatistics.total,
          good: this.annotationStatistics.taskStatistics.good,
          goodMarked:
            this.annotationStatistics.taskStatistics.good +
            " " +
            "(" +
            (
              this.annotationStatistics.taskStatistics.good /
              (this.annotationStatistics.taskStatistics.total === 0
                ? 1
                : this.annotationStatistics.taskStatistics.total)
            ).toFixed(3) +
            ")",
          bad: this.annotationStatistics.taskStatistics.bad,
          badMarked:
            this.annotationStatistics.taskStatistics.bad +
            " " +
            "(" +
            (
              this.annotationStatistics.taskStatistics.bad /
              (this.annotationStatistics.taskStatistics.total === 0
                ? 1
                : this.annotationStatistics.taskStatistics.total)
            ).toFixed(3) +
            ")",
        },
      ];
      return {
        headers: headers,
        items: items,
      };
    },
    typeTable() {
      const headers = [
        {
          text: "Type",
          value: "Type",
        },
        { text: "Total", value: "total" },
        { text: "Correct", value: "goodMarked" },
        { text: "Incorrect", value: "badMarked" },
      ];
      const items = [];
      for (const [type, statisticsObj] of Object.entries(
        this.annotationStatistics.typeStatistics
      )) {
        items.push({
          Type: type,
          total: statisticsObj.total,
          good: statisticsObj.good,
          goodMarked:
            statisticsObj.good +
            " " +
            "(" +
            (
              statisticsObj.good /
              (statisticsObj.total === 0 ? 1 : statisticsObj.total)
            ).toFixed(3) +
            ")",
          bad: statisticsObj.bad,
          badMarked:
            statisticsObj.bad +
            " " +
            "(" +
            (
              statisticsObj.bad /
              (statisticsObj.total === 0 ? 1 : statisticsObj.total)
            ).toFixed(3) +
            ")",
        });
      }
      return {
        headers: headers,
        items: items,
      };
    },
    templateTable() {
      const headers = [
        {
          text: "Type",
          value: "Type",
        },
        { text: "Total", value: "total" },
        { text: "Correct", value: "goodMarked" },
        { text: "Incorrect", value: "badMarked" },
      ];
      const items = [];
      for (const [type, statisticsObj] of Object.entries(
        this.annotationStatistics.templateStatistics
      )) {
        items.push({
          Type: type,
          total: statisticsObj.total,
          good: statisticsObj.good,
          goodMarked:
            statisticsObj.good +
            " " +
            "(" +
            (
              statisticsObj.good /
              (statisticsObj.total === 0 ? 1 : statisticsObj.total)
            ).toFixed(3) +
            ")",
          bad: statisticsObj.bad,
          badMarked:
            statisticsObj.bad +
            " " +
            "(" +
            (
              statisticsObj.bad /
              (statisticsObj.total === 0 ? 1 : statisticsObj.total)
            ).toFixed(3) +
            ")",
        });
      }
      return {
        headers: headers,
        items: items,
      };
    },
  },

  components: {},
  props: ["task"],
};
</script>

<style scope></style>
