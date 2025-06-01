from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import ShoppingListItem, ShoppingList
from .serializers import ShoppingListItemSerializer


class ShoppingListItemViewSet(viewsets.ModelViewSet):
    serializer_class = ShoppingListItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ShoppingListItem.objects.filter(
            shopping_list__user=self.request.user
        )

    def perform_create(self, serializer):
        shopping_list = ShoppingList.objects.get(user=self.request.user)
        serializer.save(shopping_list=shopping_list)

    @action(detail=False, methods=["post"], url_path="bulk-create")
    def bulk_create(self, request):
        """POST /api/shopping-list/items/bulk_create/ → add multiple items at once"""
        shopping_list = ShoppingList.objects.get(user=request.user)
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        items_to_create = []
        items_to_update = []

        for item_data in serializer.validated_data:
            name = item_data["name"].strip().lower()
            unit = item_data.get("unit", "").strip()
            quantity = item_data["quantity"]

            existing_item = ShoppingListItem.objects.filter(
                shopping_list=shopping_list,
                name__iexact=name,
                unit=unit
            ).first()

            if existing_item:
                existing_item.quantity += quantity
                items_to_update.append(existing_item)
            else:
                items_to_create.append(
                    ShoppingListItem(
                        shopping_list=shopping_list,
                        name=name,
                        unit=unit,
                        quantity=quantity
                    )
                )

        if items_to_create:
            ShoppingListItem.objects.bulk_create(items_to_create)
        if items_to_update:
            ShoppingListItem.objects.bulk_update(items_to_update, ["quantity"])

        updated_items = self.get_serializer(self.get_queryset(), many=True)
        return Response(updated_items.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["delete"])
    def clear(self, request):
        """DELETE /items/clear/ → remove all items from shopping list"""
        items = self.get_queryset()
        count = items.count()
        items.delete()
        return Response(
            {"detail": f"{count} items removed."},
            status=status.HTTP_204_NO_CONTENT
        )
