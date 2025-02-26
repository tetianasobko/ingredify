from flask import request, jsonify, Blueprint

from app import db
from app.models import Ingredient


ingredient_bp = Blueprint('ingredient', __name__)


@ingredient_bp.route('/')
def list_ingredients():
    ingredients = Ingredient.query.all()

    ingredient_list = [{
        'id': ingredient.id,
        'name': ingredient.name
    } for ingredient in ingredients]

    return jsonify({'ingredients': ingredient_list})


@ingredient_bp.route('/add', methods=['POST'])
def add_ingredient():
    try:
        data = request.get_json()
        name = data.get('name')
        ingredient = Ingredient(name=name, category_id=1)
        db.session.add(ingredient)
        db.session.commit()

        ingredient = {
            "id": ingredient.id,
            "name": ingredient.name,
        }

        return jsonify({"ingredient": ingredient}), 201
    except Exception as e:
        return jsonify({"message": f"Error while adding ingredient: {e}"}), 400
