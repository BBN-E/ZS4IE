<template>
  <v-card>
    <v-snackbar v-model="snackbarSwitch" :timeout="-1">
      {{ snackbarMsg }}

      <template v-slot:action="{ attrs }">
        <v-btn color="pink" text v-bind="attrs" @click="snackbarSwitch = false">
          Close
        </v-btn>
      </template>
    </v-snackbar>
    <v-card-title>Add New Text</v-card-title>
    <v-card-text>
      <v-col v-if="inputStage === 0">
        <v-textarea
          outlined
          label="Input text here"
          v-model="stage0OriginalText"
        />
      </v-col>
      <v-col v-if="inputStage === 1">
        <v-pagination
          v-model="stage1FocusSentenceIdPlusOne"
          :length="stage1Extraction.sentences.length"
        ></v-pagination>
        <v-card
          outlined
          v-if="
            stage1FocusSentenceIdPlusOne - 1 <
              stage1Extraction.sentences.length &&
            stage1Extraction.sentences[stage1FocusSentenceIdPlusOne - 1].tokens
          "
        >
          <v-card-text>
            <v-col>
              <h3>
                <span
                  v-for="(token, idx) in stage1Extraction.sentences[
                    stage1FocusSentenceIdPlusOne - 1
                  ].tokens"
                  :key="idx"
                  :style="annotationCalculateCSS(token)"
                  @click="changeFocusTokenIdx(token.token_idx)"
                  ><span v-text="token.text"> </span
                  ><sub v-text="getTokenEndType(token.token_idx)"></sub
                  ><span v-text="' '"></span>
                </span>
              </h3>
            </v-col>
          </v-card-text>
          <v-card-actions>
            <v-select
              :items="spanTypes"
              label="Span Type"
              v-model="selectedSpanType"
            />
            <v-text-field
              label="OntologyName"
              @focus="toggleTagging(false)"
              @blur="toggleTagging(true)"
              v-model="spanOntologyName"
            />
            <v-btn @click="tagSpan()">Apply Tag</v-btn>
            <v-btn @click="clearSpan()">Remove Tag</v-btn></v-card-actions
          >
        </v-card>
      </v-col>
    </v-card-text>
    <v-card-actions
      ><v-spacer />
      <v-btn v-if="inputStage === 0" @click="processOriginalText()"
        >Start span marking</v-btn
      >
      <v-btn v-if="inputStage === 1" @click="inputStage = 0"
        >Go back to original text</v-btn
      >
      <v-btn v-if="inputStage === 1" @click="addToDocCollection()"
        >Add to doc collection</v-btn
      ></v-card-actions
    >
  </v-card>
</template>

<script>
import constants from "@/constants/main";
import service from "@/service/main";
import _ from "lodash";
import store from "@/store/index.js";
export default {
  name: "InputProvidingBox",
  store,
  beforeDestroy() {
    if (this.inputStage === 1) {
      this.toggleTagging(false);
    }
  },
  data() {
    return {
      inputStage: 0,
      stage0OriginalText: "",
      stage1FocusSentenceIdPlusOne: 1,
      stage1Extraction: constants.exampleExtraction,
      snackbarMsg: "",
      snackbarSwitch: false,
      spanTypes: ["EventMention", "Mention"],
      selectedSpanType: null,
      spanOntologyName: "",
      tokenIdxToType: {},
      focusIdx: -1,
      selectedTokenIdxes: [],
    };
  },
  methods: {
    toggleTagging: function (enabled) {
      if (!enabled) {
        window.removeEventListener("keypress", this.annotationKeyboardHandler);
      } else {
        window.addEventListener("keypress", this.annotationKeyboardHandler);
      }
    },
    annotationCalculateCSS(token) {
      const ret = {};
      if (
        this.tokenIdxToType[token.token_idx] &&
        this.tokenIdxToType[token.token_idx].Mention
      ) {
        for (const t of Object.keys(
          this.tokenIdxToType[token.token_idx].Mention
        )) {
          _.merge(ret, this.entityTypeStyles[t]);
        }
      }
      if (
        this.tokenIdxToType[token.token_idx] &&
        this.tokenIdxToType[token.token_idx].EventMention
      ) {
        for (const t of Object.keys(
          this.tokenIdxToType[token.token_idx].EventMention
        )) {
          _.merge(ret, this.eventTypeStyles[t]);
        }
      }
      if (token.token_idx === this.focusIdx) {
        _.merge(ret, this.focusTokenStyles);
      }
      if (this.selectedTokenIdxes.includes(token.token_idx)) {
        _.merge(ret, this.selectedTokenStyles);
      }
      return ret;
    },
    changeFocusTokenIdx(tokenIdx) {
      this.focusIdx = tokenIdx;
    },
    getTokenEndType(tokenIdx) {
      let entityTypes = [];
      let eventTypes = [];
      if (
        this.tokenIdxToType[tokenIdx] &&
        this.tokenIdxToType[tokenIdx]["endTokenEntityType"]
      ) {
        entityTypes = this.tokenIdxToType[tokenIdx].endTokenEntityType;
      }
      if (
        this.tokenIdxToType[tokenIdx] &&
        this.tokenIdxToType[tokenIdx]["endTokenEventType"]
      ) {
        eventTypes = this.tokenIdxToType[tokenIdx].endTokenEventType;
      }
      return (
        (entityTypes.length < 1 ? "" : "[" + entityTypes.join(",") + "]") +
        (eventTypes.length < 1 ? "" : "[" + eventTypes.join(",") + "]")
      );
    },
    getFirstElementFromSet(set_ins) {
      for (const elem of set_ins.keys()) {
        return elem;
      }
      return null;
    },
    computeJointSpan() {
      const ret = [];
      const selectedTokenIdxesLocal = new Set(this.selectedTokenIdxes);
      const currentSentence =
        this.stage1Extraction.sentences[this.stage1FocusSentenceIdPlusOne - 1];
      let buf = [];
      for (let mover = 0; mover < currentSentence.tokens.length; mover++) {
        if (selectedTokenIdxesLocal.has(mover)) {
          if (buf.length < 1) {
            buf.push(mover);
            buf.push(mover);
          } else {
            if (buf[1] === mover - 1) {
              buf[1] = mover;
            } else {
              ret.push(buf);
              buf = [mover, mover];
            }
          }
        }
      }
      if (buf.length > 0) {
        ret.push(buf);
      }
      return ret;
    },
    clearSpan() {
      if (!this.spanTypes.includes(this.selectedSpanType)) return;
      const currentSentence =
        this.stage1Extraction.sentences[this.stage1FocusSentenceIdPlusOne - 1];
      if (!currentSentence.unary_markings) {
        currentSentence.unary_markings = {
          mentions: [],
          event_mentions: [],
        };
      }
      if (this.selectedSpanType === "Mention") {
        const newSpan = [];
        for (const span of currentSentence.unary_markings.mentions) {
          if (span.entity_type !== this.spanOntologyName) {
            newSpan.push(span);
          }
        }
        currentSentence.unary_markings.mentions = newSpan;
      } else if (this.selectedSpanType === "EventMention") {
        const newSpan = [];
        for (const span of currentSentence.unary_markings.event_mentions) {
          if (span.event_type !== this.spanOntologyName) {
            newSpan.push(span);
          }
        }
        currentSentence.unary_markings.event_mentions = newSpan;
      }
      this.reassembleTokenIdxToType();
    },
    tagSpan() {
      if (!this.spanTypes.includes(this.selectedSpanType)) return;
      const currentSentence =
        this.stage1Extraction.sentences[this.stage1FocusSentenceIdPlusOne - 1];
      if (!currentSentence.unary_markings) {
        currentSentence.unary_markings = {
          mentions: [],
          event_mentions: [],
        };
      }
      const spans = this.computeJointSpan();
      this.clearSpan();
      if (this.selectedSpanType === "Mention") {
        for (const span of spans) {
          currentSentence.unary_markings.mentions.push({
            start: span[0],
            end: span[1],
            mention_type: "name",
            entity_type: this.spanOntologyName,
          });
        }
      } else if (this.selectedSpanType === "EventMention") {
        for (const span of spans) {
          currentSentence.unary_markings.event_mentions.push({
            start: span[0],
            end: span[1],
            event_type: this.spanOntologyName,
          });
        }
      }
      this.selectedTokenIdxes = [];
      this.reassembleTokenIdxToType();
    },
    processOriginalText() {
      const originalText = this.stage0OriginalText;
      this.showSnackBarMessage("Processing text through tokenization. ");
      service.processOriginalTextStep0(originalText).then(
        (success) => {
          this.stage1Extraction = success.data.extraction;
          this.stage1SerifXMLStr = success.data.serif_doc;
          this.selectedTokenIdxes = [];
          this.focusIdx = -1;
          this.reassembleTokenIdxToType();
          this.inputStage = 1;
          this.stage1FocusSentenceIdPlusOne = 1;

          this.$store.commit("updatePreviouslyAnnotatedStep1JSONDoc", {
            previouslyAnnotatedStep1JSONDoc: _.cloneDeep(this.stage1Extraction),
          });
          this.$store.commit("updatePreviouslyAnnotatedStep1SerifXML", {
            previouslyAnnotatedStep1SerifXML: _.cloneDeep(
              this.stage1SerifXMLStr
            ),
          });
          this.hideSnackBar();
        },
        (fail) => {
          console.log(fail);
          this.hideSnackBar();
        }
      );
    },
    showSnackBarMessage(message) {
      this.snackbarMsg = message;
      this.snackbarSwitch = true;
    },
    hideSnackBar() {
      this.snackbarSwitch = false;
    },
    reassembleTokenIdxToType() {
      this.tokenIdxToType = {};
      const currentSentence =
        this.stage1Extraction.sentences[this.stage1FocusSentenceIdPlusOne - 1];
      if (!currentSentence || !currentSentence.unary_markings) {
        return;
      }

      const ret = this.tokenIdxToType;
      for (const entitySpan of currentSentence.unary_markings.mentions) {
        const start = entitySpan.start;
        const end = entitySpan.end;
        const entityType = entitySpan.entity_type;
        for (let mover = start; mover <= end; mover++) {
          if (!ret[mover]) ret[mover] = {};
          if (!ret[mover].Mention) ret[mover].Mention = {};
          ret[mover].Mention[entityType] = 1;
        }
        if (!ret[end].endTokenEntityType) ret[end].endTokenEntityType = [];
        ret[end].endTokenEntityType.push(entityType);
      }
      for (const eventSpan of currentSentence.unary_markings.event_mentions) {
        const start = eventSpan.start;
        const end = eventSpan.end;
        const eventType = eventSpan.event_type;
        for (let mover = start; mover <= end; mover++) {
          if (!ret[mover]) ret[mover] = {};
          if (!ret[mover].EventMention) ret[mover].EventMention = {};
          ret[mover].EventMention[eventType] = 1;
        }
        if (!ret[end].endTokenEventType) ret[end].endTokenEventType = [];
        ret[end].endTokenEventType.push(eventType);
      }
      return;
    },
    addToDocCollection() {
      this.$store.commit("updatePreviouslyAnnotatedStep1JSONDoc", {
        previouslyAnnotatedStep1JSONDoc: _.cloneDeep(this.stage1Extraction),
      });
      this.$store.commit("updatePreviouslyAnnotatedStep1SerifXML", {
        previouslyAnnotatedStep1SerifXML: _.cloneDeep(this.stage1SerifXMLStr),
      });
      this.$store.commit("changeAnnotationCollection", {
        task: "add",
        newAnnotationEntry: {
          a2t_extraction: _.cloneDeep(this.stage1Extraction),
          step_1_marking_extraction: _.cloneDeep(this.stage1Extraction),
          step_1_serifxml: _.cloneDeep(this.stage1SerifXMLStr),
          select_for_scoring: true,
        },
      });
      this.inputStage = 0;
      this.stage0OriginalText = "";
    },
    annotationKeyboardHandler(event) {
      const key = event.key;
      if (this.stage1Extraction.sentences.length < 1) return;
      if (this.focusIdx === -1) {
        this.focusIdx = 0;
        return;
      }
      switch (key) {
        case "d":
        case "D":
          if (
            this.focusIdx !==
            this.stage1Extraction.sentences[
              this.stage1FocusSentenceIdPlusOne - 1
            ].tokens.length -
              1
          ) {
            this.focusIdx++;
          }
          break;
        case "a":
        case "A":
          if (this.focusIdx > 0) {
            this.focusIdx--;
          }
          break;
        case "[":
        case "{":
          if (this.stage1FocusSentenceIdPlusOne > 1)
            this.stage1FocusSentenceIdPlusOne--;
          break;
        case "]":
        case "}":
          if (
            this.stage1FocusSentenceIdPlusOne <
            this.stage1Extraction.sentences.length
          )
            this.stage1FocusSentenceIdPlusOne++;
          break;
        case "t":
        case "T":
          this.toggleFocusTokenToSelectedTokenArray();
          break;
      }
    },
    toggleFocusTokenToSelectedTokenArray() {
      if (!this.selectedTokenIdxes.includes(this.focusIdx)) {
        this.selectedTokenIdxes.push(this.focusIdx);
      } else {
        const index = this.selectedTokenIdxes.indexOf(this.focusIdx);
        if (index !== -1) {
          this.selectedTokenIdxes.splice(index, 1);
        }
      }
    },
  },
  computed: {
    selectedTokenStyles() {
      return constants.spanStyles.selected_token;
    },
    focusTokenStyles() {
      return constants.spanStyles.focus_token;
    },
    entityTypeStyles() {
      const candidates = new Set(this.candidateUnaryStyles);
      const defaultStyleType = this.getFirstElementFromSet(candidates);
      candidates.delete(defaultStyleType);
      const entityTypeToStyle = {};
      for (const entityType of this.allEntityTypes) {
        if (entityType in entityTypeToStyle) continue;
        if (candidates.size < 1)
          entityTypeToStyle[entityType] =
            constants.spanStyles.unary[defaultStyleType];
        else {
          const selectedStyleType = this.getFirstElementFromSet(candidates);
          candidates.delete(selectedStyleType);
          entityTypeToStyle[entityType] =
            constants.spanStyles.unary[selectedStyleType];
        }
      }
      return entityTypeToStyle;
    },
    eventTypeStyles() {
      const candidates = new Set(this.candidateUnaryStyles);
      const defaultStyleType = this.getFirstElementFromSet(candidates);
      candidates.delete(defaultStyleType);
      const eventTypeToStyle = {};
      for (const eventType of this.allEventTypes) {
        if (eventType in eventTypeToStyle) continue;
        if (candidates.size < 1)
          eventTypeToStyle[eventType] =
            constants.spanStyles.unary[defaultStyleType];
        else {
          const selectedStyleType = this.getFirstElementFromSet(candidates);
          candidates.delete(selectedStyleType);
          eventTypeToStyle[eventType] =
            constants.spanStyles.unary[selectedStyleType];
        }
      }
      return eventTypeToStyle;
    },
    candidateUnaryStyles() {
      return new Set(Object.keys(constants.spanStyles.unary));
    },
    allEntityTypes() {
      const ret = new Set();
      for (const sentence of this.stage1Extraction.sentences) {
        for (const en of sentence.unary_markings.mentions) {
          ret.add(en.entity_type);
        }
      }
      return ret;
    },
    allEventTypes() {
      const ret = new Set();

      for (const sentence of this.stage1Extraction.sentences) {
        for (const en of sentence.unary_markings.event_mentions) {
          ret.add(en.event_type);
        }
      }
      return ret;
    },
  },
  watch: {
    inputStage(newVal, oldVal) {
      if (newVal === 1) {
        this.toggleTagging(true);
      } else {
        this.toggleTagging(false);
      }
    },
  },
};
</script>
