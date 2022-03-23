<template>
  <div>
    <v-card v-for="(constraint, idx) in input_constraints" :key="idx">
      <v-card-text>
        <!-- <p>{{ constraint.name }}</p> -->
        <div v-if="constraint.name === 'MentionTypeFilter'">
          <p
            v-for="(allowEntityPair, idx2) in constraint.args
              .allowed_mention_types"
            :key="idx2"
          >
            <span>{{ allowEntityPair }}</span>
          </p>
        </div>
        <div
          v-if="
            constraint.name === 'PairMentionEntityTypeMentionEntityTypeFilter'
          "
        >
          <p
            v-for="(allowEntityPair, idx2) in constraint.args
              .allowed_mention_entity_type_pairs"
            :key="idx2"
          >
            <span>{{ allowEntityPair[0] }}</span
            ><span> -> </span>
            <span>{{ allowEntityPair[1] }}</span>
          </p>
        </div>
        <div v-if="constraint.name === 'EventTypeArgEntityTypeFilter'">
          <p
            v-for="(allowEntityPair, idx2) in constraint.args
              .allowed_event_type_entity_type_pairs"
            :key="idx2"
          >
            <span>{{ allowEntityPair[0] }}</span>
            <span> -> </span>
            <span>{{ allowEntityPair[1] }}</span>
          </p>
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>
<script>
export default {
  name: "ConstraintBoard",
  props: [
    "input_constraints",
    "taskName",
    "ontologyName",
    "isGlobalConstraint",
    "use_global_input_constraints",
  ],
  data() {
    return {};
  },
  computed: {},
};
</script>
<style></style>
