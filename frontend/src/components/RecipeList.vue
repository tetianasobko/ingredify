<template>
  <nav>
    <router-link to="/">Home</router-link>
    <router-link to="/recipes/add">Add New Recipe</router-link>
  </nav>
  <table>
    <tr v-for="recipe in recipes">
      <td>
        <div class="recipe-card" @click="goToRecipeDetail(recipe.id)">
          <img src="/default_recipe.svg" alt="Recipe Image" class="recipe-image" />
          <div class="recipe-info">
            <h2 class="recipe-name">{{ recipe.name }}</h2>
          </div>
        </div>
        </td>
    </tr>
  </table>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      recipes: []
    };
  },
  async created() {
    try {
      const response = await axios.get('http://localhost:5000/api/recipes/');
      this.recipes = response.data.recipes;
    } catch (error) {
      console.error("Error fetching recipes", error);
    }
  },
  methods: {
    goToRecipeDetail(recipe_id) {
      this.$router.push({ name: 'recipe-detail', params: { id: recipe_id } });
    }
  }
};
</script>

<style scoped>
.recipe-card {
  width: 300px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
  transition: transform 0.3s, box-shadow 0.3s;
  margin: 20px;
  background: rgba(255, 255, 255, 0.05);
}

.recipe-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.2);
}

.recipe-image {
  width: 100%;
  height: 350px;
  border-radius: 12px;
  object-fit: cover;
}

.recipe-info {
  padding: 10px;
  text-align: center;
}

.recipe-name {
  font-size: 1.2rem;
  margin: 0;
}
</style>