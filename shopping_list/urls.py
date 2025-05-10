from django.urls import path, include
from rest_framework.routers import DefaultRouter

from shopping_list.views import ShoppingListItemViewSet

router = DefaultRouter()
router.register("items", ShoppingListItemViewSet, basename="shoppinglist_item")
urlpatterns = [
    path("", include(router.urls))
]

app_name = "shopping_list"
