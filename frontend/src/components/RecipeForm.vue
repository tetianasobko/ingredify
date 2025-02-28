<template>
  <div class="recipe-detail">
    <div v-if="isLoading" class="overlay">
      <div class="loader"></div>
    </div>
    <section class="hero">
      <img :src="heroImage" :alt="recipe.name || 'Recipe Image'"
           class="hero-image" />
      <div class="hero-overlay">
        <input
          v-model="recipe.name"
          class="recipe-title"
          placeholder="Enter recipe name"
        />
        <div class="recipe-timer">15 mins</div>
      </div>
    </section>

    <!-- Main Content Section -->
    <section class="content">
      <!-- Manual Entry Column -->
      <div class="manual-entry">
        <h1>Recipe Details</h1>

        <!-- Recipe Type Section -->
        <div class="section types">
          <h2>Type</h2>
          <div class="button-group">
            <button
              v-for="type in types"
              :key="type.id"
              @click="toggleType(type)"
              :class="{ selected: recipe.types.some(t => String(t.id) === String(type.id)) }"
            >
              {{ type.name }}
            </button>
          </div>
        </div>

        <!-- Ingredients Section -->
        <div class="section ingredients">
          <h2>Ingredients</h2>
          <div class="ingredient-input">
            <input
              v-model="newIngredient"
              list="ingredient-list"
              placeholder="Add ingredient"
              @change="onIngredientSelect"
              @input="filterIngredients"
              @keyup.enter="addIngredient"
              class="input-field"
            />
            <datalist id="ingredient-list">
              <option
                v-for="ing in filteredIngredients"
                :key="ing.id"
                :value="ing.name"
              >
                {{ ing.name }}
              </option>
            </datalist>
            <button class="btn" @click="addIngredient">+ Add</button>
          </div>
          <ul class="ingredient-list">
            <li v-for="(ing, index) in recipe.ingredients" :key="index"
                class="ingredient-item">
              <span class="ingredient-name">{{ ing.name }}</span>
              <input v-model="ing.amount" class="input-field small"
                     placeholder="Amt" />
              <input v-model="ing.unit" class="input-field small"
                     placeholder="Unit" />
              <button class="btn delete-btn" @click="removeIngredient(index)">
                ×
              </button>
            </li>
          </ul>
        </div>

        <!-- Instructions Section -->
        <div class="section instructions">
          <h2>Preparation Steps</h2>
          <textarea
            v-model="recipe.steps"
            class="textarea-field"
            placeholder="Enter instructions..."
            ref="textareaEl"
            @keyup="setHeight"
            @click="setHeight"
          ></textarea>
        </div>
      </div>

      <!-- Extraction Column -->
      <div class="extract" v-if="!recipeId">
        <h1>Extract Recipe</h1>
        <div class="button-group">
          <label class="file-label" v-if="!imageUrl">
            <input type="file" accept="image/*" @change="handleImageUpload" />
            Choose an Image
          </label>
          <button v-if="imageFile" class="btn process-btn"
                  @click="processImage">
            Process Image
          </button>
        </div>
        <div v-if="imageUrl" class="image-preview">
          <button class="delete-image-btn" @click="deleteImage">ˣ</button>
          <img :src="imageUrl" alt="Uploaded Image" />
        </div>
      </div>
    </section>

    <!-- Unified CTA Buttons -->
    <section class="cta-buttons">
      <div class="recipe-manual-buttons">
        <button class="cta-btn save-btn" @click="saveRecipe">Save Changes
        </button>
        <!--      <button class="cta-btn" @click="addToShoppingList">Add to Shopping List-->
        <!--      </button>-->
      </div>
      <div class="recipe-extract-buttons">

      </div>
    </section>
  </div>
</template>

<script>
import pluralize from 'pluralize'
import axios from 'axios'

export default {
  data() {
    return {
      heroImage: '/default_recipe.svg',
      recipeId: null,
      isLoading: false,
      recipe: {
        id: null,
        name: '',
        types: [],
        ingredients: [],
        steps: ''
      },
      types: [],
      ingredientsAll: [],
      newIngredient: '',
      filteredIngredients: [],
      imageFile: null,
      imageUrl: null
    }
  },
  async created() {
    this.recipeId = this.$route.params.id
    try {
      const res = await axios.get('http://localhost:5000/api/types/')
      this.types = res.data.types
    } catch (e) {
      console.error('Error fetching types:', e)
    }
    try {
      const res = await axios.get('http://localhost:5000/api/ingredients/')
      this.ingredientsAll = res.data.ingredients
    } catch (e) {
      console.error('Error fetching ingredients:', e)
    }
    if (this.recipeId) {
      try {
        const res = await axios.get(`http://localhost:5000/api/recipes/${this.recipeId}`)
        this.recipe = res.data.recipe
      } catch (e) {
        console.error('Error fetching recipe:', e)
      }
    }
  },
  mounted() {
    this.$nextTick(() => this.setHeight())
  },
  methods: {
    pluralize,
    handleImageUpload(event) {
      const file = event.target.files[0]
      if (file) {
        this.imageFile = file
        this.imageUrl = URL.createObjectURL(file)
      }
    },
    deleteImage() {
      this.imageFile = null
      this.imageUrl = null
    },
    async processImage() {
      this.isLoading = true

      if (!this.imageFile) {
        this.isLoading = false
        return
      }

      const formData = new FormData()
      formData.append('image', this.imageFile)
      try {
        const res = await axios.post('http://localhost:5000/api/recipes/process-image', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        const recipe = res.data.recipe
        console.log(recipe)

        this.recipe = {
          id: null,
          name: '',
          types: [],
          ingredients: [],
          steps: ''
        }

        recipe.ingredients.forEach((ingredient) => {
          this.newIngredient = ingredient.name
          this.addIngredient(ingredient.amount, ingredient.unit)
        })

        recipe.types.forEach((type) => {
          this.toggleType(type)
        })

        this.recipe.name = recipe.name
        this.recipe.steps = recipe.steps
        this.$nextTick(() => this.setHeight())

        console.log(this.recipe)

      } catch (e) {
        console.error('Error processing image:', e)
      } finally {
        this.isLoading = false
      }
    },
    toggleType(type) {
      const idx = this.recipe.types.findIndex(t => t.id === type.id)
      if (idx === -1) {
        this.recipe.types.push(type)
      } else {
        this.recipe.types.splice(idx, 1)
      }
    },
    filterIngredients() {
      if (!this.newIngredient.trim()) {
        this.filteredIngredients = []
      } else {
        this.filteredIngredients = this.ingredientsAll.filter(ing =>
          ing.name.toLowerCase().includes(this.newIngredient.toLowerCase())
        )
      }
    },
    onIngredientSelect() {
      this.$nextTick(() => {
        this.filteredIngredients = []
      })
    },
    async addIngredient(amount=undefined, unit=undefined) {
      const trimmed = pluralize.singular(this.newIngredient.trim().toLowerCase())
      if (!trimmed) return
      let existing = this.ingredientsAll.find(ing => ing.name.toLowerCase() === trimmed)
      if (!existing) {
        try {
          const res = await axios.post('http://localhost:5000/api/ingredients/add', { name: trimmed })
          const { id, name } = res.data.ingredient
          const newIng = {
            id,
            name: name.toLowerCase(),
            amount: amount,
            unit: unit
          }
          this.ingredientsAll.push(newIng)
          this.recipe.ingredients.push(newIng)
        } catch (e) {
          console.error('Error adding ingredient:', e)
        }
      } else {
        if (!this.recipe.ingredients.find(ing => ing.name.toLowerCase() === trimmed)) {
          this.recipe.ingredients.push({
            id: existing.id,
            name: existing.name.toLowerCase(),
            amount: amount,
            unit: unit
          })
        }
      }
      this.newIngredient = ''
      this.filteredIngredients = []
    },
    removeIngredient(index) {
      this.recipe.ingredients.splice(index, 1)
    },
    async saveRecipe() {
      if (!this.recipe.name || !this.recipe.ingredients.length || !this.recipe.steps) {
        alert('Please fill in the recipe details.')
        return
      }
      for (const ing of this.recipe.ingredients) {
        if (!ing.amount || isNaN(ing.amount)) {
          alert(`Invalid amount for ${ing.name}`)
          return
        }
      }
      const payload = {
        name: this.recipe.name,
        source: '',
        steps: this.recipe.steps,
        ingredients: this.recipe.ingredients,
        types: this.recipe.types.map(t => t.id)
      }
      try {
        if (this.recipeId) {
          await axios.put(`http://localhost:5000/api/recipes/edit/${this.recipe.id}`, payload)
        } else {
          const res = await axios.post(`http://localhost:5000/api/recipes/add`, payload)
          this.recipe.id = res.data.recipe_id
        }
        this.$router.push({
          name: 'recipe-detail',
          params: { id: this.recipe.id }
        })
      } catch (e) {
        console.error('Error saving recipe:', e)
      }
    },
    // addToShoppingList() {
    //   console.log('Adding ingredients to shopping list:', this.recipe.ingredients)
    // },
    setHeight() {
      const textarea = this.$refs.textareaEl
      if (textarea) {
        textarea.style.height = ''
        textarea.style.height = `${textarea.scrollHeight}px`
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
  margin-bottom: 20px;
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
  margin: 5px 10px 10px;
  width: 90%;
}

.recipe-title::placeholder {
  color: #aaa;
}

.recipe-timer {
  margin: 5px 15px 0;
  border-radius: 5px;
  font-size: 0.9em;
}

/* Content Section */
.content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.manual-entry, .extract {
  background-color: var(--card-bg);
  padding: 0 15px;
  border-radius: 8px;
}

/* Section Headings */
.manual-entry h1,
.extract h1 {
  margin-bottom: 15px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color);
  font-size: 1.5em;
}

h2 {
  margin-bottom: 8px;
  padding-bottom: 4px;
  border-bottom: 1px solid var(--border-color);
  font-size: 1.2em;
}

/* Inputs & Textareas */
.input-field,
.textarea-field {
  width: 100%;
  padding: 12px 8px;
  background-color: #444;
  color: var(--text-color);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 1em;
}

.input-field.small {
  width: 60px;
}

.textarea-field {
  min-height: 120px;
  resize: vertical;
}

/* Button Groups */
.button-group, .cta-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.recipe-manual-buttons {
  flex: 1;
  display: flex;
  justify-content: start;
  gap: 20px;
  margin-top: 20px;
}

.cta-buttons {
  margin: 15px 0 15px 15px;
  gap: 20px;
}

.recipe-extract-buttons {
  flex: 1;
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

/* Unified Button Styles */
.btn,
.file-label,
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

button.selected {
  color: white;
  border-color: #008CBA;
}

.delete-btn {
  border-radius: 100%;
  border: none;
  margin: 0;
}

.save-btn,
.file-label,
.process-btn {
  border-color: #747bff;
  margin: 10px 0;
}

.file-label {
  padding: 8px 15px;
}

.file-label input {
  display: none;
}

.btn:hover,
.file-label:hover,
.cta-btn:hover {
  background-color: #1a1a1a;
  border-color: #747bff;
}

.delete-btn:hover {
  background-color: rgba(50, 50, 50, 0.75);
}

.save-btn:hover,
.file-label:hover {
  border-color: #7e30ff;
}

/* Ingredient List */
.ingredient-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.ingredient-item {
  display: flex;
  align-items: center;
  gap: 10px;
  background-color: #333;
  padding: 5px 10px 5px 15px;
  margin: 10px 0;
  border-radius: 10px;
  width: 75%;
}

.ingredient-name {
  flex: 1;
  font-weight: bold;
}

/* Image Preview */
.image-preview {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 0 auto; /* Centers only the image preview */
  width: fit-content;

}

.image-preview img {
  display: block;
  width: 500px;
  border-radius: 4px;
}

.delete-image-btn {
  position: absolute;
  top: 5px;
  right: 5px;
  width: 40px;
  height: 40px;
  padding: 0;
  margin: 0;
  border: none;
  border-radius: 50%;
  background-color: transparent;
  color: #2a2a2a;
  font-size: 32px;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.3s ease;
  box-sizing: border-box;
}

/* Fullscreen Overlay */
.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(50, 50, 50, 0.3); /* Darkened Background */
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

/* Loading Spinner */
.loader {
  width: 50px;
  height: 50px;
  border: 5px solid rgba(255, 255, 255, 0.3);
  border-top: 5px solid #fff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* Spinner Animation */
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
