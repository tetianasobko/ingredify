<template>
  <div class="recipe-detail">
    <div class="hero-image">
      <img src="/default_recipe.svg" :alt="recipe.name" />
      <div class="overlay">
        <input v-model="recipe.name" class="edit-input title-input" />
        <div class="info">
          <span>15 mins</span>
        </div>
      </div>
    </div>

    <div class="types">
      <div class="type-buttons">
        <button
          v-for="type in types"
          :key="type.name"
          @click="toggleType(type)"
          :class="{ selected: recipe.types.some(t => t.id === type.id) }"
        >
          {{ type.name }}
        </button>
      </div>
    </div>

    <!-- Ingredients Section -->
    <div class="ingredients">
      <h2>Ingredients</h2>
      <input
        v-model="newIngredient"
        list="ingredient-list"
        placeholder="Enter the ingredient"
        ref="ingredientEl"
        @change="onIngredientSelect"
        @input="filterIngredients"
        @keyup.enter="addIngredient"
        class="custom-input edit-input small"
      />
      <datalist id="ingredient-list">
        <option v-for="ingredient in filteredIngredients" :key="ingredient.id" :value="ingredient.name">{{ingredient.name}}</option>
      </datalist>
      <button @click="addIngredient" class="add-btn">+ Add Ingredient</button>
      <ul class="ingredient-list">
        <li v-for="(ingredient, index) in recipe.ingredients" :key="index" class="ingredient-item">
          <span class="ingredient-name">{{ingredient.name}}</span>
          <input v-model="ingredient.amount" class="edit-input very-small" placeholder="Amount" />
          <input v-model="ingredient.unit" class="edit-input very-small" placeholder="Unit" />
          <button @click="removeIngredient(index)" class="delete-btn">X</button>
        </li>
      </ul>
    </div>

    <!-- Instructions Section -->
    <div class="recipe-container">
      <div class="instructions">
        <h2>Preparation Steps</h2>
        <textarea v-model="recipe.steps" class="edit-textarea" ref="textareaEl" @keyup="setHeight" @click="setHeight"></textarea>

      </div>
    </div>

    <!-- Save to Favorites or Shopping List -->
    <div class="cta-buttons">
      <button @click="saveRecipe" class="cta-button">Save Changes</button>
      <button @click="addToShoppingList" class="cta-button">Add to Shopping List</button>
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
        types: [],
        ingredients: [],
        steps: '',
      },
      types: [],
      ingredientsAll: [],
      newIngredient: '',
      filteredIngredients: [],
      selectedUnit: null,
      unitEnum: {}
    }
  },
  async created() {
    const recipeId = this.$route.params.id;
    try {
      const response = await axios.get('http://localhost:5000/api/types/');
      this.types = await response.data.types;
    } catch (error) {
      console.error('Error fetching types:', error);
    }
    try {
       const response = await axios.get('http://localhost:5000/api/ingredients/');
       this.ingredientsAll = response.data.ingredients.slice();
     } catch (error) {
       console.error("Error fetching ingredients", error);
     }

    if (recipeId) {
      try {
        const response = await axios.get(`http://localhost:5000/api/recipes/${recipeId}`);
        this.recipe = await response.data.recipe;
      } catch (error) {
        console.error('Error fetching recipe:', error);
      }
    } else {
      this.recipe = {
        id: null,
        name: '',
        types: [],
        ingredients: [],
        steps: '',
      }
    }
  },
  watch: {
    'recipe.steps': function () {
      this.$nextTick(() => {
        this.setHeight();
      });
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.setHeight()
    });
  },
  methods: {
    toggleType(type) {
      const index = this.recipe.types.findIndex(t => t.id === type.id); // Find exact match by ID
      if (index === -1) {
        this.recipe.types.push(type);
      } else {
        this.recipe.types.splice(index, 1);
      }
    },
    onIngredientSelect() {
      this.$nextTick(() => {
        this.filteredIngredients = [];
      });
    },
    filterIngredients() {
      if (!this.newIngredient.trim()) {
        this.filteredIngredients = [];
      } else {
        this.filteredIngredients = this.ingredientsAll.filter(ingredient =>
            ingredient.name.toLowerCase().includes(this.newIngredient.toLowerCase())
        );
      }
    },
    async addIngredient() {
      const trimmed = this.newIngredient.trim().toLowerCase();
      if (!trimmed) return;

      let existingIngredient = this.ingredientsAll.find(ingredient =>
        ingredient.name.toLowerCase() === trimmed
      );

      if (!existingIngredient) {
        try {
          const response = await axios.post('http://localhost:5000/api/ingredients/add', { name: trimmed });
          const { id, name } = response.data.ingredient;
          const newIngredient = { id, name: name.toLowerCase(), amount: '', unit: '' };

          this.ingredientsAll.push(newIngredient);
          this.recipe.ingredients.push(newIngredient);
        } catch (error) {
          console.error("Error adding new ingredient to database", error);
        }
      } else {
        if (!this.recipe.ingredients.find(ingredient => ingredient.name.toLowerCase() === trimmed)) {
          this.recipe.ingredients.push({
            id: existingIngredient.id,
            name: existingIngredient.name.toLowerCase(),
            amount: '',
            unit: ''
          });
        }
      }

      this.newIngredient = '';
      this.filteredIngredients = [];
    },
    removeIngredient(index) {
      this.recipe.ingredients.splice(index, 1);
    },
    async saveRecipe() {
      if (!this.recipe.name || !this.recipe.ingredients || !this.recipe.steps) {
        alert("Recipe title, ingredients and steps are necessary!");
        return;
      }

      for (const ingredient of this.recipe.ingredients) {
        if (!ingredient.amount || ingredient.amount <= 0 || isNaN(ingredient.amount)) {
          alert(`Invalid amount! "${ingredient.name}"!`);
          return;
        }
        if (!ingredient.unit) {
          alert(`Choose unit for "${ingredient.name}"!`);
          return;
        }
      }

      const newRecipe = {
        name: this.recipe.name,
        source: "",
        steps: this.recipe.steps,
        ingredients: this.recipe.ingredients.map(ing => ({
          id: ing.id,
          name: ing.name,
          amount: ing.amount,
          unit: ing.unit
        })),
        types: this.recipe.types.map(type => type.id)
      };

      try {
        if (this.$route.params.id) {
          await axios.put(`http://localhost:5000/api/recipes/edit/${this.recipe.id}`, newRecipe);
        } else {
          // Adding a new recipe: use POST
          const response = await axios.post(`http://localhost:5000/api/recipes/add`, newRecipe);
          // Optionally, update the recipe id after creation
          this.recipe.id = response.data.recipe_id;
        }

        this.$router.push({ name: 'recipe-detail', params: { id: this.recipe.id } });
      } catch (error) {
        console.error("There is an error while saving the recipe", error);
      }
    },
    addToShoppingList() {
      console.log('Added to shopping list:', this.recipe.ingredients);
      // Send ingredients to shopping list feature
    },
    setHeight() {
      const textarea = this.$refs.textareaEl;
      textarea.style.height = "";               // Reset the height
      textarea.style.height = `${textarea.scrollHeight}px`; // Set height to fit content
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
  padding: 20px;
}

.hero-image .overlay .edit-input {
  background: transparent;
  border: none;
  color: white;
  font-size: 2.5em;
  font-weight: bold;
  margin-bottom: 10px;
  outline: none;
}

.types input {
  font-size: 1.2em;
  text-align: center;
  padding: 5px;
  width: 100%;
  border: none;
  background: #f3f3f3;
}

.ingredients, .instructions, .cta-buttons {
  padding: 20px;
  margin-bottom: 20px;
}

.ingredients ul, .instructions ol {
  list-style-type: none;
  padding-left: 0;
}

.ingredient-list {
  list-style: none;
  padding: 0;
}

.ingredient-item {
  display: flex;
  padding: 10px;
  border-radius: 8px;
  margin-bottom: 8px;
  width: 100%;
}

.ingredient-name {
  flex: 0.5;
  font-weight: 500;
  padding-left: 5px;
}

.edit-input {
  padding: 5px;
  border: 1px solid #ccc;
  border-radius: 5px;
  font-size: 1em;
}

.title-input {
  padding: 5px;
  border: 1px solid #ccc;
  border-radius: 5px;
  font-size: 1em;
  width: 100%
}

.edit-input.small {
  width: 40%;
}

.edit-input.very-small {
  width: 60px;
  text-align: center;
}

.edit-textarea {
  width: 100%;
  padding: 5px;
  border: 1px solid #ccc;
  border-radius: 5px;
  font-size: 1.2em;
  resize: none;
  overflow: auto;
}


.delete-btn {
  background: red;
  color: white;
  border: none;
  padding: 5px 10px;
  cursor: pointer;
  font-weight: bold;
  border-radius: 5px;
}

.add-btn {
  background: green;
  color: white;
  border: none;
  padding: 10px;
  cursor: pointer;
  border-radius: 5px;
  margin-top: 10px;
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

.instructions {
  flex: 1;
}

.instructions {
  padding: 20px;
  border-radius: 8px;
  max-width: 50%;
  position: relative;
}

.type-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.type-buttons button {
  padding: 10px 15px;
  border: 1px solid #ccc;
  cursor: pointer;
  border-radius: 5px;
  transition: 0.3s;
}

.type-buttons button.selected {
  color: white;
  border-color: #008CBA;
}
</style>
