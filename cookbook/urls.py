from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    RecipeViewSet,
    DietaryRestrictionViewSet,
    MealTypeListView,
    UnitListView,
    DifficultyListView,
    RecipeImageAIView,
    RecipeTextAIView,
    ChatAIView
)

router = DefaultRouter()
router.register("recipes", RecipeViewSet)
router.register("dietary-restrictions", DietaryRestrictionViewSet)
urlpatterns = [
    path("", include(router.urls)),
    path("units/", UnitListView.as_view(), name="units"),
    path("difficulties/", DifficultyListView.as_view(), name="difficulties"),
    path("meal-types/", MealTypeListView.as_view(), name="meal-types"),
    path("process-image/", RecipeImageAIView.as_view(), name="process-image"),
    path("process-text/", RecipeTextAIView.as_view(), name="process-text"),
    path("chat/", ChatAIView.as_view(), name="chat")
]

app_name = "cookbook"
