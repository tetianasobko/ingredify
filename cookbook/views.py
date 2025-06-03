import json
import os
import base64

from rest_framework import viewsets, mixins, views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from groq import Groq
from drf_spectacular.utils import extend_schema

from .models import Recipe, DietaryRestriction, MealType, Unit, Difficulty
from .serializers import (
    RecipeSerializer,
    RecipeListSerializer,
    DietaryRestrictionSerializer,
    DietaryRestrictionListSerializer
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
            return DietaryRestrictionListSerializer
        return DietaryRestrictionSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def get_queryset(self):
        queryset = super().get_queryset()  # Get the base queryset
        queryset = queryset.prefetch_related("dietary_restrictions")

        if self.action == "retrieve":
            return queryset.prefetch_related(
                "ingredients"
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RecipeListSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RecipeImageAIView(views.APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'images': {
                        'type': 'array',
                        'items': {'type': 'string', 'format': 'binary'},
                    },
                },
                'required': ['images']
            }
        }
    )
    def post(self, request):
        if not request.FILES:
            return Response(
                {"error": "No images provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            base64_images = []
            for image in request.FILES.getlist("images"):
                image_data = image.read()
                base64_image = base64.b64encode(image_data).decode("utf-8")
                base64_images.append(base64_image)

            units = list(Unit.values)
            difficulties = list(Difficulty.values)
            meal_types = list(MealType.values)
            dietary_restrictions = list(
                DietaryRestriction.objects.values_list("slug", flat=True)
            )

            json_output = {
                "title": "string",
                "cooking_time": 0,
                "prep_time": 0,
                "servings": 0,
                "difficulty": "string",
                "instructions": "string",
                "ingredients": [
                    {
                        "name": "string",
                        "quantity": 0,
                        "unit": "string"
                    }
                ],
                "meal_type": "string",
                "dietary_restrictions": [0]
            }

            prompt = (
                f"Extract the following structured data in JSON format from the recipe below. Make sure to follow these strict rules:\n"
                f"JSON Format:\n"
                f"{json.dumps(json_output)}"
                f"Constraints:\n"
                f"difficulty must be one of: {', '.join(difficulties)}\n"
                f"meal_type must be one of: {', '.join(meal_types)}\n"
                f"unit must be one of: {', '.join(units)}\n"
                f"dietary_restrictions must be a list of integers representing IDs from list: {dietary_restrictions}\n"
                f"Do not include any values outside these allowed options. Use reasonable approximations if exact units or labels are not mentioned in the text."
            )

            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]

            # Add each image to the message content
            for base64_image in base64_images:
                messages[0]["content"].append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                })

            client = Groq(
                api_key=os.environ.get("GROQ_API_KEY"),
            )

            completion = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=messages,
                temperature=1,
                max_completion_tokens=1024,
                top_p=1,
                stream=False,
                response_format={"type": "json_object"},
                stop=None,
            )

            recipe = completion.choices[0].message.content

            data = json.loads(recipe)
            return Response({
                "message": f"{len(base64_images)} images processed successfully",
                "data": data,
            }, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
