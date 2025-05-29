from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    RecipeViewSet,
    DietaryRestrictionViewSet,
    MealTypeListView,
    UnitListView,
    DifficultyListView
)

router = DefaultRouter()
router.register("recipes", RecipeViewSet)
router.register("dietary-restrictions", DietaryRestrictionViewSet)
urlpatterns = [
    path("", include(router.urls)),
    path("units/", UnitListView.as_view(), name="units"),
    path("difficulties/", DifficultyListView.as_view(), name="difficulties"),
    path("meal-types/", MealTypeListView.as_view(), name="meal-types"),
]

app_name = "cookbook"
