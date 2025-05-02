from rest_framework import viewsets

from ingredify.models import Recipe
from ingredify.serializers import RecipeSerializer, RecipeListSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return RecipeListSerializer
        return RecipeSerializer
