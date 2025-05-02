from django.contrib import admin
from .models import Recipe, Ingredient


class IngredientInline(admin.TabularInline):
    model = Ingredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("title", "difficulty", "cooking_time", "prep_time", "servings", "date_added")
    search_fields = ("title", "ingredients__name")
    list_filter = ("difficulty", "date_added")
    inlines = [IngredientInline]


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "quantity", "unit", "recipe")
    search_fields = ("name",)
    list_filter = ("unit",)
