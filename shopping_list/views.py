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
        shopping_list, _ = ShoppingList.objects.get(user=self.request.user)
        serializer.save(shopping_list=shopping_list)

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
