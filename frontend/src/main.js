import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import './style.css'
import App from './App.vue'
import RecipeItem from './components/RecipeItem.vue'
import RecipeList from "./components/RecipeList.vue";
import RecipeDetail from "./components/RecipeDetail.vue";
import RecipeForm from "./components/RecipeForm.vue";


const router = createRouter({
    history: createWebHistory(),
    routes: [
        { path: '/', name: 'recipe-list', component: RecipeList },
        { path: '/recipes/:id', name: 'recipe-detail', component: RecipeDetail },
        { path: '/recipes/add/', name: 'add-recipe', component: RecipeForm },
        { path: '/recipes/edit/:id', name: 'edit-recipe', component: RecipeForm },
    ]
});

const app = createApp(App)
app.component('recipe-item', RecipeItem)
app.use(router)

app.mount('#app')
