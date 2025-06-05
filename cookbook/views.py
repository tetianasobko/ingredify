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


class BaseRecipeAIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get_recipe_constraints(self):
        units = list(Unit.values)
        difficulties = list(Difficulty.values)
        meal_types = list(MealType.values)
        dietary_restrictions = list(
            DietaryRestriction.objects.values_list("id", "slug")
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

        return {
            "units": units,
            "difficulties": difficulties,
            "meal_types": meal_types,
            "dietary_restrictions": dietary_restrictions,
            "json_output": json_output
        }

    def process_with_ai(self, messages):
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=messages,
            temperature=0.5,
            max_completion_tokens=1024,
            top_p=1,
            stream=False,
            response_format={"type": "json_object"},
            stop=None,
        )
        return completion.choices[0].message.content


class RecipeImageAIView(BaseRecipeAIView):
    @extend_schema(
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "images": {
                        "type": "array",
                        "items": {"type": "string", "format": "binary"},
                    },
                },
                "required": ["images"]
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

            constraints = self.get_recipe_constraints()
            prompt = (
                f"Extract recipe data in JSON format following these strict rules:\n\n"
                f"1. Use only these units: {', '.join(constraints['units'])}\n"
                f"2. Convert common units to allowed units:\n"
                f"   - Use 'pc' (piece) for: cloves, slices, whole items\n"
                f"   - Convert volume units to 'ml'\n"
                f"   - Convert weight units to 'g'\n"
                f"3. Difficulty must be one of: {', '.join(constraints['difficulties'])}\n"
                f"4. Meal type must be one of: {', '.join(constraints['meal_types'])}\n"
                f"5. Dietary restrictions IDs from: {constraints['dietary_restrictions']}\n\n"
                f"Expected JSON format:\n{json.dumps(constraints['json_output'], indent=2)}"
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

            for base64_image in base64_images:
                messages[0]["content"].append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                })

            recipe = self.process_with_ai(messages)
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


class RecipeTextAIView(BaseRecipeAIView):
    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"}
                },
                "required": ["text"]
            }
        }
    )
    def post(self, request):
        text = request.data.get("text")
        if not text:
            return Response(
                {"error": "No text provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            constraints = self.get_recipe_constraints()
            prompt = (
                f"Extract recipe data in JSON format following these strict rules:\n\n"
                f"1. Use only these units: {', '.join(constraints['units'])}\n"
                f"2. Convert common units to allowed units:\n"
                f"   - Use 'pc' (piece) for: cloves, slices, whole items\n"
                f"3. Difficulty must be one of: {', '.join(constraints['difficulties'])}\n"
                f"4. Meal type must be one of: {', '.join(constraints['meal_types'])}\n"
                f"5. Dietary restrictions IDs from: {constraints['dietary_restrictions']}\n\n"
                f"Expected JSON format:\n{json.dumps(constraints['json_output'], indent=2)}"
            )

            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "text",
                            "text": text
                        }
                    ]
                }
            ]

            recipe = self.process_with_ai(messages)
            data = json.loads(recipe)
            return Response({
                "message": "Text processed successfully",
                "data": data,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ChatAIView(views.APIView):
    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "messages": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "role": {
                                    "type": "string",
                                    "enum": ["user", "assistant"]
                                },
                                "content": {"type": "string"}
                            }
                        }
                    }
                },
                "required": ["messages"]
            }
        },
        responses={200: {"type": "object"}}
    )
    def post(self, request):
        try:
            client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

            completion = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=request.data["messages"],
                temperature=0.7,
                max_completion_tokens=1024,
                top_p=1,
                stream=False,
            )

            response = completion.choices[0].message.content
            return Response({"message": response}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
