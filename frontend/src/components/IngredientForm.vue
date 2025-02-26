<template>
  <div class="ingredient-selector">
    <label for="ingredient">Оберіть інгредієнт:</label>
    <input
      v-model="newIngredient"
      list="ingredient-list"
      placeholder="Введіть або виберіть..."
      @input="filterIngredients"
      @keyup.enter="addIngredient"
      class="custom-input"
    />
    <datalist id="ingredient-list">
      <option v-for="ingredient in filteredIngredients" :key="ingredient.id" :value="ingredient.name">{{ingredient.name}}</option>
    </datalist>
    <button @click="addIngredient">Додати</button>

    <ul>
      <li v-for="(ingredient, index) in selectedIngredients" :key="index">
        {{ ingredient.name }} <button @click="removeIngredient(index)">&times;</button>
      </li>
    </ul>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      newIngredient: '',
      ingredients: [],
      filteredIngredients: [],
      selectedIngredients: []
    };
  },
  async created() {
     try {
       const response = await axios.get('http://localhost:5000/api/ingredients/');
       this.ingredients = response.data.ingredients.slice();
     } catch (error) {
       console.error("Error fetching ingredients", error);
     }
  },
  methods: {
    filterIngredients() {
      this.filteredIngredients = this.ingredients.filter(ingredient =>
        ingredient.name.toLowerCase().includes(this.newIngredient.toLowerCase())
      );
    },
    async addIngredient() {
      const trimmed = this.newIngredient.trim().toLowerCase();
      if (!trimmed) return;

      let existingIngredient = this.ingredients.find(ingredient =>
        ingredient.name.toLowerCase() === trimmed
      );

      if (!existingIngredient) {
        if (!this.selectedIngredients.find(ing => ing.name.toLowerCase() === trimmed)) {
          this.selectedIngredients.push(existingIngredient);
        }
      } else {
        try {
          const response = await axios.post('http://localhost:5000/api/ingredients/add', { name: trimmed });
          const newIngredientObj = response.data.ingredient;
          this.ingredients.push(newIngredientObj);
          this.selectedIngredients.push(newIngredientObj);
        } catch (error) {
          console.error("Error adding new ingredient to database", error);
        }
      }

      this.newIngredient = '';
      this.filteredIngredients = [];
    },
    removeIngredient(index) {
      this.selectedIngredients.splice(index, 1);
    }
  }
};
</script>

<style scoped>
.ingredient-selector {
  max-width: 300px;
  margin: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.custom-input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  outline: none;
}
</style>
