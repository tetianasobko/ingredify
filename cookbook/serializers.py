from django.db import transaction
from rest_framework import serializers

from .models import Ingredient, Recipe, DietaryRestriction


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "quantity", "unit")


class DietaryRestrictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DietaryRestriction
        fields = ("id", "name", "slug")


class DietaryRestrictionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DietaryRestriction
        fields = ("name",)


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "title",
            "image",
            "cooking_time",
            "prep_time",
            "servings",
            "difficulty",
            "date_added",
            "instructions",
            "ingredients",
            "meal_type",
            "dietary_restrictions",
        )

    @transaction.atomic
    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        dietary_restrictions = validated_data.pop(
            "dietary_restrictions", []
        )
        recipe = Recipe.objects.create(**validated_data)
        recipe.dietary_restrictions.set(dietary_restrictions)
        for ingredient_data in ingredients_data:
            Ingredient.objects.create(recipe=recipe, **ingredient_data)
        return recipe


class RecipeListSerializer(RecipeSerializer):
    dietary_restrictions = DietaryRestrictionListSerializer(
        many=True, read_only=True
    )

    class Meta:
        model = Recipe
        fields = (
            "id",
            "title",
            "image",
            "cooking_time",
            "prep_time",
            "difficulty",
            "meal_type",
            "dietary_restrictions",
        )


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
