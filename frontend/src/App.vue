<template>
<div id="app">
    <router-view></router-view>  <!-- Displays the current page based on the route -->
  </div>
</template>



<script>
import {defineComponent} from "vue";
import RecipeList from "./components/RecipeList.vue";

export default defineComponent({
  components: {RecipeList}
})
</script>

<style>
</style>