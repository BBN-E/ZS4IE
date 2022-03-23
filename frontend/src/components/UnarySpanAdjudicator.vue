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
        <p
          :class="{
            goodInstance: annotationEntry.isFrozen && annotationEntry.isGood,
            badInstance: annotationEntry.isFrozen && !annotationEntry.isGood,
          }"
        >
          <span
            v-for="(token, token_idx) in annotationEntry.summary.originalSpan"
            :key="'left' + token_idx"
            :style="token.style"
          >
            {{ token.text }}
          </span>
          <span> is a/an </span>
          <span> {{ annotationEntry.summary.type }} </span>
          <span>{{ " " }}</span>
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
  name: "UnarySpanAdjudicator",
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
      const careTokenSpans = new Set();
      const originalAnnotationEntries = [];
      for (const sentence of this.jsonDoc.sentences) {
        if (this.task === "NER") {
          for (const entityMention of sentence.mentions) {
            if (entityMention.model !== "Ask2Transformers") continue;
            careTokenSpans.add(
              sentence.sent_no +
                "#" +
                entityMention.start_token_idx +
                "#" +
                entityMention.end_token_idx
            );
            const tokenArr = [];
            for (
              let i = entityMention.start_token_idx;
              i <= entityMention.end_token_idx;
              ++i
            ) {
              tokenArr.push({
                text: sentence.tokens[i].text,
                style: {},
                tokenId: sentence.sent_no + "#" + i,
              });
            }
            originalAnnotationEntries.push({
              summary: {
                originalSpan: tokenArr,
                type: entityMention.entity_type,
              },
              originalObject: entityMention,
              isFrozen: entityMention.is_frozen,
              isGood: entityMention.is_good,
              patternEntries: JSON.parse(entityMention.pattern),
            });
          }
        } else if (this.task === "EventMention") {
          for (const eventMention of sentence.event_mentions) {
            if (eventMention.model !== "Ask2Transformers") continue;
            careTokenSpans.add(
              sentence.sent_no +
                "#" +
                eventMention.start_token_idx +
                "#" +
                eventMention.end_token_idx
            );
            const tokenArr = [];
            for (
              let i = eventMention.start_token_idx;
              i <= eventMention.end_token_idx;
              ++i
            ) {
              tokenArr.push({
                text: sentence.tokens[i].text,
                style: {},
                tokenId: sentence.sent_no + "#" + i,
              });
            }
            originalAnnotationEntries.push({
              summary: {
                originalSpan: tokenArr,
                type: eventMention.event_type,
              },
              originalObject: eventMention,
              isFrozen: eventMention.is_frozen,
              isGood: eventMention.is_good,
              patternEntries: JSON.parse(eventMention.pattern_id),
            });
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
        for (const token of originalAnnotationEntry.summary.originalSpan) {
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
