import json
import os
import base64
import re
import requests
from django.db.models.functions.text import Lower

from rest_framework import viewsets, mixins, views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from groq import Groq
from drf_spectacular.utils import extend_schema
from urllib.parse import quote_plus

from shopping_list.models import ShoppingList, ShoppingListItem
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
            constraints = self.get_recipe_constraints()
            prompt = (
                f"Extract recipe data in JSON format following these strict rules:\n\n"
                f"1. Use only these units: {', '.join(constraints['units'])}\n"
                f"2. Convert common units to allowed units:\n"
                f"   - Use 'pc' (piece) for: cloves, slices, whole items\n"
                f"3. ALL numbers must be decimal values (no fractions)"
                f"4. Difficulty must be one of: {', '.join(constraints['difficulties'])}\n"
                f"5. Meal type must be one of: {', '.join(constraints['meal_types'])}\n"
                f"6. Dietary restrictions IDs from: {constraints['dietary_restrictions']}\n\n"
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

            for image in request.FILES.getlist("images"):
                image_data = image.read()
                base64_image = base64.b64encode(image_data).decode("utf-8")
                messages[0]["content"].append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                })

            recipe = self.process_with_ai(messages)
            data = json.loads(recipe)
            return Response({
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
                f"3. ALL numbers must be decimal values (no fractions)"
                f"4. Difficulty must be one of: {', '.join(constraints['difficulties'])}\n"
                f"5. Meal type must be one of: {', '.join(constraints['meal_types'])}\n"
                f"6. Dietary restrictions IDs from: {constraints['dietary_restrictions']}\n\n"
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


def get_recipes(
        title: str = None,
        cook_time: int = None,
        servings: int = None,
        difficulty: str = None,
        dietary_restrictions: list = None,
        meal_type: str = None,
        ingredients: list = None
):
    queryset = Recipe.objects.all()
    filters = {}

    if title:
        filters["title__icontains"] = str(title)
    if cook_time:
        filters["cooking_time__lte"] = int(cook_time)
    if servings:
        filters["servings__gte"] = int(servings)
    if difficulty:
        filters["difficulty"] = str(difficulty)
    if dietary_restrictions:
        filters["dietary_restrictions__in"] = dietary_restrictions
    if meal_type:
        filters["meal_type"] = str(meal_type)
    if ingredients:
        filters["ingredients__name__in"] = ingredients

    return list(queryset.filter(**filters).distinct().values(
        "id",
        "title",
        "cooking_time",
        "servings",
        "difficulty",
        "meal_type",
        "dietary_restrictions__name",
        "ingredients__name"
    )[:10])


_UA_CHAR_PATTERN = re.compile(r"[А-Яа-яЄєІіЇїҐґ]")


def is_ukrainian(text: str) -> bool:
    return bool(_UA_CHAR_PATTERN.search(text))


def detect_language(text: str) -> str:
    return "uk" if is_ukrainian(text) else "en"


def get_product_prices(products: list[str]) -> list[dict]:
    session = requests.Session()
    store_id = "48201070"
    base_url = f"https://stores-api.zakaz.ua/stores/{store_id}/products/search/"

    results: list[dict] = []

    for raw_name in products:
        lang = detect_language(raw_name)
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "Accept-Language": lang,
        }

        query_string = quote_plus(raw_name)
        url = f"{base_url}?q={query_string}"

        try:
            resp = session.get(url, headers=headers, timeout=5)
            resp.raise_for_status()
            data = resp.json()
        except (requests.RequestException, ValueError) as exc:
            continue

        for prod_item in data.get("results", [])[:5]:
            title = prod_item.get("title")
            price_cents = prod_item.get("price")
            unit = prod_item.get("unit", "")
            weight = prod_item.get("weight", "")

            if title is None or price_cents is None:
                continue

            results.append({
                "title": title,
                "price": price_cents / 100,
                "currency": "uah",
                "unit": unit,
                "weight": weight,
            })

    return results


def get_prices_for_recipe_titles(recipe_titles: list[str]):
    lowered_titles = [title.lower() for title in recipe_titles]

    recipes = list(
        Recipe.objects.annotate(lower_title=Lower("title"))
        .filter(lower_title__in=lowered_titles)
    )

    response = []

    for recipe in recipes:
        recipe_data = {
            "id": recipe.id,
            "title": recipe.title,
            "ingredients": []
        }

        for ingredient in recipe.ingredients.all():
            store_products = get_product_prices([ingredient.name])

            recipe_data["ingredients"].append({
                "name": ingredient.name,
                "quantity": ingredient.quantity,
                "unit": ingredient.unit,
                "store_products": store_products,
            })

        response.append(recipe_data)

    return json.dumps(response, ensure_ascii=False)


def handle_recipes_response(response_data: list[dict]) -> dict:
    return {
        "recipes": [
            recipe.get("id") for recipe in response_data if "id" in recipe
        ]
    }


class ChatAIView(views.APIView):
    def _get_shopping_list_item_prices(self):
        items = list(
            ShoppingListItem.objects
            .filter(shopping_list__user=self.request.user)
        )

        response = []

        for item in items:
            store_products = get_product_prices([item.name])

            response.append({
                "name": item.name,
                "quantity": item.quantity,
                "unit": item.unit,
                "store_products": store_products,
            })
        return json.dumps(response, ensure_ascii=False)

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
            incoming = request.data.get("messages")
            if not isinstance(incoming, list) or not incoming:
                return Response(
                    {
                        "error": "Payload must include a non-empty 'messages' list."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            user_lang = detect_language(incoming[0].get("content", ""))

            system_prompt = (
                "You are a helpful cooking assistant."
                "Always respond in the same language the user uses."
                "Never transliterate or change the script of product names."
                "For example, if the user writes 'йогурт з манго' in Ukrainian, keep it exactly "
                "in Ukrainian Cyrillic."
                f"Respond in {user_lang} language."
            )

            messages = [
                {"role": "system", "content": system_prompt}
            ] + incoming

            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "get_recipes",
                        "description": "Get recipes based on user preferences and constraints",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "string",
                                    "description": "Search by recipe title"
                                },
                                "cook_time": {
                                    "type": "integer",
                                    "description": "Maximum cooking time"
                                },
                                "servings": {
                                    "type": "integer",
                                    "description": "Minimum servings"
                                },
                                "difficulty": {
                                    "type": "string",
                                    "enum": list(Difficulty.values)
                                },
                                "meal_type": {
                                    "type": "string",
                                    "enum": list(MealType.values)
                                },
                                "dietary_restrictions": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "ingredients": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                            }
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_product_prices",
                        "description": (
                            "Get average price for each product."
                            "Do not return ranges."
                            "All information you use to formulate your "
                            "responses must come exclusively from the outputs "
                            "of the provided tools."
                            "Must match the user's query language."
                            "Convert the product name to singular form."
                            "Format the output naturally as a sentence."

                        ),
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "products": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_prices_for_recipe_titles",
                        "description": (
                            "Calculate how much it costs to make a specific recipe or list of recipes. "
                            "For each recipe, list the ingredients with their individual average prices first, "
                            "then display the total cost to make the recipe. "
                            "Use this to estimate the full cost of preparing a dish based on its ingredients. "
                            "Do NOT use this to look up individual product prices. "
                            "Use only when the user asks about the cost of making a recipe by name (e.g. 'How much does it cost to make Banilla Splash?')."
                            "Must match the user's query language."
                        ),
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "recipe_titles": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of recipe titles to get prices for"
                                }
                            }
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_shopping_list_item_prices",
                        "description": (
                            "Get the user's shopping list items with their average prices."
                            "Must match the user's query language."
                        ),
                        "parameters": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                }
            ]

            api_key = os.environ.get("GROQ_API_KEY")
            if not api_key:
                return Response(
                    {"error": "GROQ_API_KEY is not set in the environment."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            client = Groq(api_key=api_key)
            model = "deepseek-r1-distill-llama-70b"

            first_response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_completion_tokens=1024,
                tools=tools,
                tool_choice="auto"
            )

            message_obj = first_response.choices[0].message

            if not getattr(message_obj, "tool_calls", None):
                return Response(
                    {"message": message_obj.content},
                    status=status.HTTP_200_OK
                )

            return self._run_tools_and_respond(
                client=client,
                model=model,
                messages=messages,
                initial_message=message_obj,
                tool_calls=message_obj.tool_calls,
                tools=tools
            )

        except Exception as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _run_tools_and_respond(
            self,
            client,
            model: str,
            messages: list,
            initial_message,
            tool_calls: list,
            tools: list
    ) -> Response:
        available_functions = {
            "get_recipes": get_recipes,
            "get_product_prices": get_product_prices,
            "get_prices_for_recipe_titles": get_prices_for_recipe_titles,
            "get_shopping_list_item_prices": self._get_shopping_list_item_prices
        }

        handlers = {
            "get_recipes": handle_recipes_response,
        }

        messages.append({
            "role": "assistant",
            "content": initial_message.content or "",
            "tool_calls": [tc.to_dict() for tc in tool_calls]
        })

        additional_messages = {}
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(**function_args)

            additional_messages.update(
                handlers[function_name](
                    function_response
                ) if function_name in handlers else {}
            )

            messages.append({
                "role": "tool",
                "content": json.dumps(function_response),
                "tool_call_id": tool_call.id
            })

        final_resp = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            max_completion_tokens=4096
        )

        final_message = final_resp.choices[0].message.content

        combined_output = {"message": final_message, **additional_messages}

        return Response(combined_output, status=status.HTTP_200_OK)
