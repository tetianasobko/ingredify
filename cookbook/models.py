import os
import pathlib
import uuid

from django.db import models
from django.utils.text import slugify

from ingredify_service import settings


# Units for ingredients
class Unit(models.TextChoices):
    GRAM = "g", "gram"
    MILLILITER = "ml", "milliliter"
    TEASPOON = "tsp", "teaspoon"
    TABLESPOON = "tbsp", "tablespoon"
    PIECE = "pc", "piece"


class Difficulty(models.TextChoices):
    EASY = "easy", "Easy"
    MEDIUM = "medium", "Medium"
    HARD = "hard", "Hard"


class MealType(models.TextChoices):
    BREAKFAST = "breakfast", "Breakfast"
    LUNCH = "lunch", "Lunch"
    DINNER = "dinner", "Dinner"
    APPETIZER = "appetizer", "Appetizer"
    SNACK = "snack", "Snack"
    DESSERT = "dessert", "Dessert"
    DRINK = "drink", "Drink"
    SIDE = "side", "Side Dish"


class DietaryRestriction(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


def recipe_image_path(recipe: "Recipe", filename: str) -> pathlib.Path:
    _, ext = os.path.splitext(filename)
    filename = f"{slugify(recipe.title)}-{uuid.uuid4()}{ext}"
    return pathlib.Path("upload/recipes") / pathlib.Path(filename)


# Recipe
class Recipe(models.Model):
    title = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    image = models.ImageField(
        upload_to=recipe_image_path,
        blank=True,
        null=True
    )
    cooking_time = models.IntegerField()
    prep_time = models.IntegerField()
    servings = models.IntegerField()
    difficulty = models.CharField(
        max_length=20, choices=Difficulty.choices
    )
    dietary_restrictions = models.ManyToManyField(
        DietaryRestriction,
        blank=True,
        related_name="recipes"
    )

    meal_type = models.CharField(
        max_length=20,
        choices=MealType.choices,
    )
    date_added = models.DateTimeField(auto_now_add=True)
    instructions = models.TextField()

    class Meta:
        ordering = ["-date_added"]

    def __str__(self):
        return self.title


# Ingredient in a recipe
class Ingredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, related_name="ingredients", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    quantity = models.FloatField()
    unit = models.CharField(max_length=20, choices=Unit.choices)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"
