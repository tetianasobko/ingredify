from rest_framework import viewsets, mixins, views
from rest_framework.response import Response

from .models import Recipe, DietaryRestriction, MealType, Unit, Difficulty
from .serializers import (
    RecipeSerializer,
    RecipeListSerializer,
    DietaryRestrictionSerializer
)


class UnitListView(views.APIView):
    def get(self, request):
        return Response(
            [{"value": u.value, "label": u.label} for u in Unit]
        )


class DifficultyListView(views.APIView):
    def get(self, request):
        return Response(
            [{"value": d.value, "label": d.label} for d in Difficulty]
        )


class MealTypeListView(views.APIView):
    def get(self, request):
        return Response(
            [{"value": m.value, "label": m.label} for m in MealType]
        )


class DietaryRestrictionViewSet(
    mixins.ListModelMixin, viewsets.GenericViewSet
):
    queryset = DietaryRestriction.objects.all()
    serializer_class = DietaryRestrictionSerializer

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return DietaryRestrictionSerializer
        return DietaryRestrictionSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return RecipeListSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
