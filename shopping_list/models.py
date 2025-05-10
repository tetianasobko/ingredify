from django.db import models

from cookbook.models import Unit
from ingredify_service import settings


class ShoppingList(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="shopping_list",
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.user}'s Shopping List"


class ShoppingListItem(models.Model):
    shopping_list = models.ForeignKey(
        ShoppingList, related_name="items", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    quantity = models.FloatField()
    unit = models.CharField(max_length=20, choices=Unit.choices)
    checked = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} {self.quantity}{self.unit}"
