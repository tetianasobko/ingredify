<template>
  <section class="recipe-detail">
    <section class="hero">
      <img :src="heroImage" :alt="recipe.name || 'Recipe Image'"
           class="hero-image" />
      <div class="hero-overlay">
        <h1 class="recipe-title">{{ recipe.name || 'Recipe Name' }}</h1>
        <div class="recipe-timer">15 mins</div>
      </div>
    </section>

    <section class="content">
      <div class="button-group types">
        <button v-for="type in recipe.types" :key="type.id" class="type-btn">{{ type.name }}
        </button>
      </div>

      <!-- Ingredients Section -->
      <div class="section ingredients">
        <h2>Ingredients</h2>
        <ul>
          <li v-for="(ingredient, index) in recipe.ingredients" :key="index">
            <span>{{ ingredient.amount }} {{ ingredient.unit
              }} {{ pluralize(ingredient.name, ingredient.amount) }}</span>
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
    </section>
    <section class="cta-buttons">
      <button @click="editRecipe" class="cta-btn">Edit</button>
      <button @click="deleteRecipe" class="cta-btn">Delete</button>
    </section>
  </section>
</template>

<script>
import pluralize from 'pluralize'
import axios from 'axios'

export default {
  data() {
    return {
      heroImage: '/default_recipe.svg',
      recipe: {
        id: null,
        name: '',
        // imageUrl: '',
        servings: '',
        type: { name: '' },
        ingredients: [],
        steps: ''
      }
    }
  },
  async created() {
    const recipeId = this.$route.params.id

    if (recipeId) {
      try {
        const response = await axios(`http://localhost:5000/api/recipes/${recipeId}`)
        this.recipe = response.data.recipe
        console.log(this.recipe)
      } catch (error) {
        console.error('Error fetching recipe:', error)
      }
    }
  },
  methods: {
    pluralize,
    editRecipe() {
      this.$router.push({
        name: 'edit-recipe',
        params: { id: this.recipe.id }
      })
    },
    async deleteRecipe() {
      try {
        await axios.delete(`http://localhost:5000/api/recipes/delete/${this.recipe.id}`)
        this.$router.push({ name: 'recipe-list' })
      } catch (error) {
        console.error('Error deleting recipe:', error)
      }
    }
  }
}
</script>

<style scoped>
:root {
  --bg-color: #1f1f1f;
  --card-bg: #2a2a2a;
  --primary: #620ea;
  --primary-hover: #7e30ff;
  --text-color: #e0e0e0;
  --border-color: #555;
}

/* Outer Container */
.recipe-detail {
  background-color: var(--bg-color);
  color: var(--text-color);
  width: 100%;
  border-radius: 10px;
  font-family: 'Helvetica Neue', Arial, sans-serif;
}

/* Hero Section */
.hero {
  position: relative;
  width: 100%;
  height: 600px;
}

.hero-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0.9;
}

.hero-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  background: rgba(0, 0, 0, 0.75);
  padding: 10px 0;
  justify-content: space-between;
  align-items: center;
}

.recipe-title {
  background: transparent;
  border: none;
  color: var(--text-color);
  font-size: 1.8em;
  font-weight: bold;
  margin: 5px 15px 10px;
  padding: 1px;
}

.recipe-title::placeholder {
  color: #aaa;
}

.recipe-timer {
  margin: 16px 15px 0;
  border-radius: 5px;
  font-size: 0.9em;
}

/* Content Section */
.content {
  margin: 20px 0 20px;
  padding: 0 15px 8px;
}

.recipe-container {
  display: flex;
  flex-wrap: wrap;
  gap: 10%;
  justify-content: space-between;
  padding-right: 7%;
}

.instructions, .notes {
  flex: 1;
}

.instructions {
  flex: 2;
  padding: 20px 0;
  border-radius: 8px;
  width: 400px;
}

.notes {
  flex: 1;
  margin-top: 15px;
  padding: 5px 20px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  max-width: 350px;
}

/* Section Headings */
.content h1 {
  margin-bottom: 15px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color);
  font-size: 1.5em;
  background-color: var(--card-bg);
  border-radius: 8px;
}

h2 {
  margin-bottom: 8px;
  padding-bottom: 4px;
  border-bottom: 1px solid var(--border-color);
  font-size: 1.2em;
}

/* Button Groups */
.button-group, .cta-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.cta-buttons {
  margin: 15px;
}

/* Ingredient List */
.ingredients ul, .instructions ol {
  list-style-type: none;
  padding-left: 0;
}

.ingredients li {
  margin-bottom: 10px;
}

/* Unified Button Styles */
.cta-btn {
  background-color: var(--primary);
  border: 1px solid grey;
  color: #fff;
  border-radius: 8px;
  padding: 10px 15px;
  cursor: pointer;
  transition: background 0.3s ease;
  font-size: 1em;
  margin-bottom: 10px;
  margin-top: 10px;
}

.cta-btn:hover {
  background-color: #1a1a1a;
  border-color: #747bff;
}

.type-btn {
  border-radius: 20px;
}
</style>
