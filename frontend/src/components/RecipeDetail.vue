<template>
  <div class="recipe-detail">
    <div class="hero-image">
      <img src="/default_recipe.svg" :alt="recipe.name"/>
      <div class="overlay">
        <h1>{{ recipe.name }}</h1>
        <div class="info">
          <span><i class="fa fa-clock"></i> 15 mins</span>
        </div>
      </div>
    </div>

    <div class="types">
      <button v-for="type in recipe.types">{{ type.name }}</button>
    </div>

    <!-- Ingredients Section -->
    <div class="ingredients">
      <h2>Ingredients</h2>
      <ul>
        <li v-for="(ingredient, index) in recipe.ingredients" :key="index">
          <span>{{ ingredient.name }} - {{
              ingredient.amount
            }} {{ ingredient.unit }}</span>
        </li>
      </ul>
    </div>

    <!-- Instructions Section -->
    <div class="recipe-container">
      <div class="instructions">
        <h2>Preparation Steps</h2>
        <ol>
          <li v-for="(step, index) in recipe.steps.split('\n')" :key="index">
            <p>{{ step }}</p>
          </li>
        </ol>
      </div>
      <div class="notes">
        <h2>Notes</h2>
        <ul>
          <li>Some</li>
          <li>Useful</li>
          <li>Notes</li>
        </ul>
      </div>
    </div>

    <!-- Save to Favorites or Shopping List -->
    <div class="cta-buttons">
      <button @click="editRecipe" class="cta-button">Edit</button>
      <button @click="deleteRecipe" class="cta-button">Delete</button>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      recipe: {
        id: null,
        name: '',
        // imageUrl: '',
        servings: '',
        type: {name: ''},
        ingredients: [],
        steps: '',
      }
    };
  },
  async created() {
    const recipeId = this.$route.params.id;

    if (recipeId) {
      try {
        const response = await axios(`http://localhost:5000/api/recipes/${recipeId}`);
        this.recipe = response.data.recipe;
        console.log(this.recipe)
      } catch (error) {
        console.error('Error fetching recipe:', error);
      }
    }
  },
  methods: {
    editRecipe() {
      this.$router.push({name: 'edit-recipe', params: {id: this.recipe.id}});
    },
    async deleteRecipe() {
      try {
        const response = await axios.delete(`http://localhost:5000/api/recipes/delete/${this.recipe.id}`);
        this.$router.push({name: 'recipe-list'});
      } catch (error) {
        console.error('Error deleting recipe:', error);
      }
    }
  },
};
</script>

<style scoped>
.recipe-detail {
  max-width: 100%;
  margin: 0 auto;
}

.hero-image {
  position: relative;
  width: 100%;
  height: 600px;
}

.hero-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-image .overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: end;
  align-items: flex-start;
  text-align: center;
}

.hero-image .overlay h1 {
  font-size: 2.5em;
  margin-left: 20px;
  margin-bottom: 10px;
}

.hero-image .overlay .info {
  font-size: 1.2em;
  margin-left: 20px;
  margin-bottom: 10px;
}

.ingredients, .instructions, .cta-buttons {
  padding: 20px;
  margin-bottom: 20px;
}

.ingredients ul, .instructions ol {
  list-style-type: none;
  padding-left: 0;
}

.ingredients li {
  margin-bottom: 10px;
}

.cta-buttons button {
  padding: 10px 20px;
  font-size: 1em;
  background-color: #008CBA;
  color: white;
  border: none;
  cursor: pointer;
  margin-right: 10px;
}

.cta-buttons button:hover {
  background-color: #005f75;
}

.recipe-container {
  display: flex;
  gap: 20px;
}

.instructions, .notes {
  flex: 1;
}

.instructions {
  padding: 20px;
  border-radius: 8px;
  max-width: 50%;
}

.notes {
  padding: 20px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  max-width: 300px;

}
</style>
