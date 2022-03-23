<template>
  <v-app id="app">
    <v-app-bar app color="primary" dark>
      <!-- <v-app-bar-nav-icon @click="drawer = true"></v-app-bar-nav-icon> -->
      <div class="d-flex align-center"></div>
      <v-spacer></v-spacer>
    </v-app-bar>
    <v-navigation-drawer v-model="drawer" absolute temporary>
      <v-list nav dense>
        <v-list-item-group active-class="deep-purple--text text--accent-4">
        </v-list-item-group>
      </v-list>
    </v-navigation-drawer>
    <v-main class="main_view">
      <router-view class="main_view" />
    </v-main>
  </v-app>
</template>

<script>
import store from "@/store/index.js";
export default {
  name: "App",
  store,
  data: () => ({
    drawer: false,
  }),
  mounted() {
    this.$store.dispatch("fetchDefaultA2TConfig").then((success) => {
      this.$store.commit("changeFocusTaskEntry", { focusType: "NER" });
    });
  },
  methods: {
    toggleOntologyPanel() {
      this.$store.commit("toggleDisplayOntologyPanel");
    },
    switchRoute(viewName) {
      this.$router.replace({ name: viewName });
    },
  },
};
</script>

<style>
/*html,*/
/*body,*/
/*#app,*/
/*.main_view*/
/*{*/
/*  width: 100% !important;*/
/*  height: 100vh !important;*/
/*  overflow: hidden !important;*/
/*}*/
</style>
