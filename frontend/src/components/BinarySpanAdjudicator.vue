<template>
  <v-col>
    <v-card outlined>
      <v-card-text>
        <p
          v-for="(sentence, sent_idx) in markedJSONDoc.sentences"
          :key="'sent' + sent_idx"
        >
          <span
            v-for="(token, token_idx) in sentence.tokens"
            :key="token_idx"
            :style="token.style"
          >
            {{ token.text }}
          </span>
        </p>
      </v-card-text>
    </v-card>
    <v-card
      v-for="(
        annotationEntry, annotationEntryIdx
      ) in markedJSONDoc.annotationEntries"
      :key="'anno' + annotationEntryIdx"
      outlined
    >
      <v-card-text
        :class="{
          goodInstance: annotationEntry.isFrozen && annotationEntry.isGood,
          badInstance: annotationEntry.isFrozen && !annotationEntry.isGood,
        }"
      >
        <p>
          <span
            v-for="(token, token_idx) in annotationEntry.summary.left"
            :key="'left' + token_idx"
            :style="token.style"
          >
            {{ token.text }}
          </span>
          <span>{{ " " }}</span>
          <span> {{ annotationEntry.summary.type }} </span>
          <span>{{ " " }}</span>
          <span
            v-for="(token, token_idx) in annotationEntry.summary.right"
            :key="'right' + token_idx"
            :style="token.style"
          >
            {{ token.text }}
          </span>
        </p>

        <table style="width: 100%">
          <thead>
            <tr>
              <th>Type</th>
              <th>Template</th>
              <th>Score</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(
                patternEntry, patternEntryIdx
              ) in annotationEntry.patternEntries"
              :key="patternEntryIdx"
            >
              <td>{{ patternEntry[0] }}</td>
              <td>{{ patternEntry[1] }}</td>
              <td>{{ patternEntry[2].toFixed(3) }}</td>
            </tr>
          </tbody>
        </table>

        <v-btn icon @click="changeAnnotation(annotationEntry, false, false)"
          ><v-icon>mdi-close</v-icon></v-btn
        >
        <v-btn icon @click="changeAnnotation(annotationEntry, true, false)"
          ><v-icon>mdi-minus</v-icon></v-btn
        >
        <v-btn icon @click="changeAnnotation(annotationEntry, true, true)"
          ><v-icon>mdi-plus</v-icon></v-btn
        >
      </v-card-text>
    </v-card>
  </v-col>
</template>

<script>
import store from "@/store/index.js";
import constants from "@/constants/main";
import _ from "lodash";
export default {
  name: "BinarySpanAdjudicator",
  store,
  data() {
    return {};
  },
  methods: {
    changeAnnotation(element, isFrozen, isGood) {
      if (!isFrozen) {
        element.originalObject.is_frozen = false;
        element.originalObject.is_good = isGood;
      } else {
        element.originalObject.is_frozen = true;
        element.originalObject.is_good = isGood;
      }
    },
    getNextStyleDict(seedObj) {
      const currentIdx = seedObj.seed;
      seedObj.seed++;
      return this.stylePool[currentIdx % this.stylePool.length];
    },
  },
  mounted() {},
  computed: {
    stylePool() {
      const ret = [];
      const keyArr = Array.from(Object.keys(constants.spanStyles.unary));
      keyArr.sort();
      for (const key of keyArr) {
        ret.push(constants.spanStyles.unary[key]);
      }
      return ret;
    },
    markedJSONDoc() {
      const seedObj = { seed: 0 };
      const mentionIdToMentionDict = {};
      const mentionIdToSentenceDict = {};
      for (const sentence of this.jsonDoc.sentences) {
        for (const mention of sentence.mentions) {
          const mentionId = mention.mention_id;
          mentionIdToMentionDict[mentionId] = mention;
          mentionIdToSentenceDict[mentionId] = sentence;
        }
      }
      const careTokenSpans = new Set();
      const originalAnnotationEntries = [];
      if (this.task === "Relation") {
        for (const entityRelation of this.jsonDoc.entity_relations) {
          if (entityRelation.model !== "Ask2Transformers") continue;
          const leftMentionId = entityRelation.left_mention_id;
          const rightMentionId = entityRelation.right_mention_id;
          const leftSentence = mentionIdToSentenceDict[leftMentionId];
          const rightSentence = mentionIdToSentenceDict[rightMentionId];
          const relationType = entityRelation.rel_type;
          const leftMention = mentionIdToMentionDict[leftMentionId];
          const rightMention = mentionIdToMentionDict[rightMentionId];
          const leftMentionTokenStartIdx = leftMention.start_token_idx;
          const leftMentionTokenEndIdx = leftMention.end_token_idx;
          const leftSentenceId = leftSentence.sent_no;
          careTokenSpans.add(
            leftSentenceId +
              "#" +
              leftMentionTokenStartIdx +
              "#" +
              leftMentionTokenEndIdx
          );
          const leftTokenArray = [];
          for (
            let i = leftMentionTokenStartIdx;
            i <= leftMentionTokenEndIdx;
            ++i
          ) {
            leftTokenArray.push({
              text: leftSentence.tokens[i].text,
              style: {},
              tokenId: leftSentenceId + "#" + i,
            });
          }
          const rightMentionTokenStartIdx = rightMention.start_token_idx;
          const rightMentionTokenEndIdx = rightMention.end_token_idx;
          const rightSentenceId = rightSentence.sent_no;
          careTokenSpans.add(
            rightSentenceId +
              "#" +
              rightMentionTokenStartIdx +
              "#" +
              rightMentionTokenEndIdx
          );
          const rightTokenArray = [];
          for (
            let i = rightMentionTokenStartIdx;
            i <= rightMentionTokenEndIdx;
            ++i
          ) {
            rightTokenArray.push({
              text: rightSentence.tokens[i].text,
              style: {},
              tokenId: rightSentenceId + "#" + i,
            });
          }
          originalAnnotationEntries.push({
            summary: {
              left: leftTokenArray,
              right: rightTokenArray,
              type: relationType,
            },
            originalObject: entityRelation,
            isFrozen: entityRelation.is_frozen,
            isGood: entityRelation.is_good,
            patternEntries: JSON.parse(entityRelation.pattern),
          });
        }
      } else if (this.task === "EventArgument") {
        for (const sentence of this.jsonDoc.sentences) {
          const leftSentence = sentence;
          for (const leftEventMention of sentence.event_mentions) {
            let shouldAppendTrigger = false;
            const leftTokenArray = [];
            for (
              let i = leftEventMention.start_token_idx;
              i <= leftEventMention.end_token_idx;
              ++i
            ) {
              leftTokenArray.push({
                text: sentence.tokens[i].text,
                style: {},
                tokenId: sentence.sent_no + "#" + i,
              });
            }
            for (const eventArg of leftEventMention.event_args) {
              if (eventArg.model !== "Ask2Transformers") continue;
              const rightMention = mentionIdToMentionDict[eventArg.ref];
              const argRole = eventArg.role;
              const rightSentence = mentionIdToSentenceDict[eventArg.ref];
              shouldAppendTrigger = true;
              careTokenSpans.add(
                rightSentence.sent_no +
                  "#" +
                  rightMention.start_token_idx +
                  "#" +
                  rightMention.end_token_idx
              );
              const rightTokenArray = [];
              for (
                let i = rightMention.start_token_idx;
                i <= rightMention.end_token_idx;
                ++i
              ) {
                rightTokenArray.push({
                  text: rightSentence.tokens[i].text,
                  style: {},
                  tokenId: rightSentence.sent_no + "#" + i,
                });
              }
              originalAnnotationEntries.push({
                summary: {
                  left: _.cloneDeep(leftTokenArray),
                  right: rightTokenArray,
                  type: argRole,
                },
                originalObject: eventArg,
                isFrozen: eventArg.is_frozen,
                isGood: eventArg.is_good,
                patternEntries: JSON.parse(eventArg.pattern),
              });
            }
            if (shouldAppendTrigger) {
              careTokenSpans.add(
                leftSentence.sent_no +
                  "#" +
                  leftEventMention.start_token_idx +
                  "#" +
                  leftEventMention.end_token_idx
              );
            }
          }
        }
      }
      const tokenIdxToStyle = {};
      for (const careTokenSpan of Array.from(careTokenSpans)) {
        const currentStyle = this.getNextStyleDict(seedObj);
        const careTokenSpanSplit = careTokenSpan.split("#");
        const sentNo = parseInt(careTokenSpanSplit[0]);
        const startTokenIdx = parseInt(careTokenSpanSplit[1]);
        const endTokenIdx = parseInt(careTokenSpanSplit[2]);
        for (let i = startTokenIdx; i <= endTokenIdx; ++i) {
          const tokenId = sentNo + "#" + i;
          if (!(tokenId in tokenIdxToStyle)) tokenIdxToStyle[tokenId] = {};
          _.merge(tokenIdxToStyle[tokenId], currentStyle);
        }
      }
      for (const originalAnnotationEntry of originalAnnotationEntries) {
        for (const token of originalAnnotationEntry.summary.left) {
          const tokenId = token.tokenId;
          _.merge(token["style"], tokenIdxToStyle[tokenId]);
        }
        for (const token of originalAnnotationEntry.summary.right) {
          const tokenId = token.tokenId;
          _.merge(token["style"], tokenIdxToStyle[tokenId]);
        }
      }
      const newThinDoc = {
        sentences: [],
        annotationEntries: originalAnnotationEntries,
      };
      for (const sentence of this.jsonDoc.sentences) {
        const newSentence = {
          sent_no: sentence.sent_no,
          tokens: [],
        };
        for (const token of sentence.tokens) {
          const tokenId = sentence.sent_no + "#" + token.token_idx;
          if (tokenId in tokenIdxToStyle) {
            newSentence.tokens.push({
              token_idx: token.token_idx,
              text: token.text,
              style: tokenIdxToStyle[tokenId],
            });
          } else {
            newSentence.tokens.push({
              token_idx: token.token_idx,
              text: token.text,
              style: {},
            });
          }
        }
        newThinDoc.sentences.push(newSentence);
      }
      return newThinDoc;
    },
    jsonDoc() {
      return this.$store.getters.annotationCollection[
        this.annotationCollectionIdx
      ].a2t_extraction;
    },
  },
  components: {},
  props: ["task", "annotationCollectionIdx"],
};
</script>

<style scope>
.goodInstance {
  background-color: #c8e6c9;
}
.badInstance {
  background-color: #ffcdd2;
}
.stickBoard {
  position: -webkit-sticky;
  position: sticky;
  top: 80px;
}
</style>
