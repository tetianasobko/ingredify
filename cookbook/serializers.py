from django.db import transaction
from rest_framework import serializers

from .models import Ingredient, Recipe


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "quantity", "unit")


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
        "id", "title", "cooking_time", "prep_time", "servings", "difficulty",
        "date_added", "instructions", "ingredients")

    @transaction.atomic
    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            Ingredient.objects.create(recipe=recipe, **ingredient_data)
        return recipe


class RecipeListSerializer(RecipeSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "title", "cooking_time")


class RecipeDetailSerializer(RecipeSerializer):
    ingredients = IngredientSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = (
        "id",
        "title",
        "cooking_time",
        "prep_time",
        "servings",
        "difficulty",
        "date_added",
        "instructions",
        "ingredients"
        )
