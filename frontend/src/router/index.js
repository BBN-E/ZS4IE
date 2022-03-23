import Vue from "vue";
import VueRouter from "vue-router";
import NewMainView from "@/components/NewMainView";

Vue.use(VueRouter);

const routes = [
  {
    path: "/",
    name: "NewMainView",
    component: NewMainView,
  },
];

const router = new VueRouter({
  routes,
});

export default router;
