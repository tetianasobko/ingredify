from django.urls import path, include
from rest_framework.routers import DefaultRouter

from ingredify.views import RecipeViewSet

router = DefaultRouter()
router.register("recipes", RecipeViewSet)
urlpatterns = [
    path("", include(router.urls)),
]

app_name = "ingredify"