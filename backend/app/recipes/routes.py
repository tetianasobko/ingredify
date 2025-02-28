import json
import logging
import os
from base64 import b64encode
from io import BytesIO

from PIL import Image

from flask import jsonify, Blueprint, request
from dotenv import load_dotenv
from app import db
from app.models import Recipe, RecipeType, Ingredient, RecipeIngredient

load_dotenv()
recipe_bp = Blueprint('recipe', __name__)


@recipe_bp.route('/process-image', methods=['POST'])
def add_with_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    from groq import Groq

    api_key = os.getenv("GROQ_API_KEY")
    client = Groq(api_key=api_key)

    # Load the image from request
    image_file = request.files['image']
    image = Image.open(image_file)

    # Convert image to base64 (optional)
    buffered = BytesIO()
    image.save(buffered, format=image.format)
    image_base64 = b64encode(buffered.getvalue()).decode()

    completion = client.chat.completions.create(
        model="llama-3.2-90b-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extract all text from the image"
                    },
                    {
                        "type": "image_url", "image_url":
                        {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }

                ]
            }
        ],
        temperature=1,
        max_completion_tokens=1024,
        top_p=1,
        stream=False,
        stop=None
    )

    recipe_text = completion.choices[0].message.content

    recipe_types = RecipeType.query.all()
    recipe_types_list = [{"id": rt.id, "name": rt.name} for rt in recipe_types]

    json_output = {
        "recipe": {
            'name': "",
            'types': [{
                "id": "",
                "name": ""
            }],
            "ingredients": [{
                "name": "",
                "amount": "",
                "unit": ""
            }],
            'steps': "",
        },
    }

    json_prompt = (
        f"Take the context and convert it into JSON following these guidelines:\n\n"
        f"Context: {recipe_text}"
        f"1. Recipe Types:\n"
        f"   - Identify the recipe type from the image and ensure that it is one of the allowed types: {recipe_types_list}.\n"
        f"   - If the extracted recipe type does not directly match any of the allowed types, select the most appropriate type from the allowed list instead of skipping.\n\n"
        f"2. Name: \n"
        f"   - Name should be capitalized.\n" 
        f"3. Steps:\n"
        f"   - Split the recipe steps into individual paragraphs using the newline character ('\\n') as a delimiter.\n\n"
        f"4. Ingredients:\n"
        f"   - For each ingredient, extract the ingredient name, the amount, and the unit.\n"
        f"   - The amount must contain only a numerical value in standard decimal format (e.g., '0.5' instead of '1/2'), with no units or fractions included.\n"
        f"   - If unit is missing, represent it as an empty string, ingredient name and amount are mandatory.\n\n"
        f"5. Final Output:\n"
        f"   - Use the following JSON structure exactly:\n{json.dumps(json_output)}\n"
        f"   - Ensure that the output is valid JSON.\n"
    )

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": json_prompt
            }
        ],
        temperature=1,
        max_completion_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
        response_format={"type": "json_object"},
    )

    recipe = json.loads(completion.choices[0].message.content)
    return jsonify(recipe)


@recipe_bp.route('/', methods=['GET'])
def list_recipes():
    recipes = Recipe.query.all()
    recipe_list = []

    for recipe in recipes:
        ingredients = [
            {
                'id': ri.ingredient.id,
                'name': ri.ingredient.name,
            }
            for ri in recipe.ingredients
        ]
        types = [
            {
                "id": rt.id,
                "name": rt.name
            }
            for rt in recipe.types
        ]

        recipe_list.append({
            'id': recipe.id,
            'name': recipe.name,
            'types': types,
            'ingredients': ingredients,
            'steps': recipe.steps,
        })

    return jsonify({"recipes": recipe_list})


@recipe_bp.route('/<int:recipe_id>', methods=["GET"])
def get_recipe(recipe_id: int):
    recipe = Recipe.query.get_or_404(recipe_id)
    ingredients = [
        {
            'id': recipe_ingredient.ingredient.id,
            'name': recipe_ingredient.ingredient.name,
            'amount': recipe_ingredient.amount,
            'unit': recipe_ingredient.unit,
        }
        for recipe_ingredient in recipe.ingredients
    ]
    types = [
        {
            "id": recipe_type.id,
            "name": recipe_type.name
        }
        for recipe_type in recipe.types
    ]

    recipe = {
        'id': recipe.id,
        'name': recipe.name,
        # 'imageUrl': recipe.image_url,
        'types': types,
        'ingredients': ingredients,
        'steps': recipe.steps,
    }

    return jsonify({"recipe": recipe})


@recipe_bp.route('/add', methods=['GET', 'POST'])
def add_recipe():
    try:
        data = request.get_json()

        if not data.get("name") or not data.get("steps") or not data.get(
                "ingredients"):
            return jsonify(
                {"error": "Recipe name, steps, and ingredients are required"}
            ), 400

        new_recipe = Recipe(
            name=data.get("name"),
            source="",  # Default value for source
            steps=data.get("steps")
        )

        types = data.get("types")
        if types:
            for type_id in types:
                recipe_type = RecipeType.query.get(type_id)
                if recipe_type:
                    new_recipe.types.append(recipe_type)

        db.session.add(new_recipe)

        ingredients = data.get("ingredients")
        if ingredients:
            for ingredient_data in ingredients:
                ingredient_name = ingredient_data.get('name')
                amount = ingredient_data.get('amount')
                unit = ingredient_data.get('unit')

                if not ingredient_name or not amount or not unit:
                    continue

                ingredient = Ingredient.query.get(ingredient_data.get("id"))

                if not ingredient:
                    return jsonify({
                        "error": f"Ingredient '{ingredient_name}' not found"}
                    ), 400

                recipe_ingredient = RecipeIngredient(
                    recipe_id=new_recipe.id,
                    ingredient_id=ingredient.id,
                    amount=float(amount),
                    unit=unit
                )
                db.session.add(recipe_ingredient)

        db.session.commit()
        return jsonify({"message": "Recipe added successfully",
                        "recipe_id": new_recipe.id}), 201
    except Exception as e:
        db.session.rollback()
        logging.info(e)
        return jsonify({"error": str(e)}), 500


@recipe_bp.route('/edit/<int:recipe_id>', methods=['PUT'])
def edit_recipe(recipe_id):
    try:
        data = request.get_json()
        recipe = Recipe.query.get_or_404(recipe_id)
        if not recipe:
            return jsonify({"error": "Recipe not found"}), 404

        recipe.name = data.get("name")
        recipe.source = ""
        recipe.steps = data.get("steps")

        types = data.get("types")
        if types:
            recipe.types.clear()
            for type_id in types:
                recipe_type = RecipeType.query.get(type_id)
                if recipe_type:
                    recipe.types.append(recipe_type)

        ingredients = data.get("ingredients")
        if ingredients:
            # Clear existing RecipeIngredient relationships
            RecipeIngredient.query.filter_by(recipe_id=recipe_id).delete()

            for ingredient_data in ingredients:
                ingredient_id = ingredient_data.get("id")
                ingredient_name = ingredient_data.get('name')
                amount = ingredient_data.get('amount')
                unit = ingredient_data.get('unit')

                if not ingredient_name or not amount or not unit:
                    continue  # Skip invalid entries

                ingredient = Ingredient.query.get(ingredient_id)

                # Create new RecipeIngredient entry
                recipe_ingredient = RecipeIngredient(
                    recipe_id=recipe.id,
                    ingredient_id=ingredient.id,
                    amount=float(amount),
                    unit=unit
                )
                db.session.add(recipe_ingredient)

        db.session.commit()
        return jsonify(
            {"message": "Recipe updated successfully", "recipe": recipe.id}
        ), 200
    except Exception as e:
        db.session.rollback()
        logging.info(e)
        return jsonify({"error": str(e)}), 500


@recipe_bp.route('/delete/<int:recipe_id>', methods=['DELETE'])
def delete_recipe(recipe_id):
    try:
        recipe = Recipe.query.get_or_404(recipe_id)

        RecipeIngredient.query.filter_by(recipe_id=recipe_id).delete()

        db.session.delete(recipe)
        db.session.commit()

        return jsonify({"message": "Recipe deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting recipe: {e}")
        return jsonify({"error": str(e)}), 500
