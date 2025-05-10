from rest_framework import serializers

from shopping_list.models import ShoppingListItem


class ShoppingListItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingListItem
        fields = ("id", "name", "quantity", "unit", "checked")
