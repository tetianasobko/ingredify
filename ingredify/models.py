from django.db import models


# Units for ingredients
class Unit(models.TextChoices):
    GRAM = "g", "gram"
    MILLILITER = "ml", "milliliter"
    TEASPOON = "tsp", "teaspoon"
    TABLESPOON = "tbsp", "tablespoon"
    PIECE = "pc", "piece"


# Recipe
class Recipe(models.Model):
    title = models.CharField(max_length=255)
    cooking_time = models.IntegerField()
    prep_time = models.IntegerField()
    servings = models.IntegerField()
    difficulty = models.CharField(max_length=50)
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
