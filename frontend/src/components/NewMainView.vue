<template>
  <v-container fluid>
    <v-card elevation="0">
      <v-card-text>
        <v-row>
          <OntologyView />
        </v-row>
        <v-row>
          <v-col>
            <InputProvidingBox />
          </v-col>
          <v-col>
            <InferenceConfig />
          </v-col>
        </v-row>
        <v-row>
          <AdjudicationBoard />
        </v-row>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
import InputProvidingBox from "@/components/InputProvidingBox";
import OntologyView from "@/components/OntologyView";
import AdjudicationBoard from "@/components/AdjudicationBoard";
import InferenceConfig from "@/components/InferenceConfig";
export default {
  name: "NewMainView",
  data() {
    return {};
  },
  computed: {},
  components: {
    InputProvidingBox,
    OntologyView,
    AdjudicationBoard,
    InferenceConfig,
  },
};
</script>

<style scope></style>
