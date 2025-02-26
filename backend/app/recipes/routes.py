import logging

from flask import jsonify, Blueprint, request

from app import db
from app.models import Recipe, RecipeType, Ingredient, RecipeIngredient


recipe_bp = Blueprint('recipe', __name__)


@recipe_bp.route('/')
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
