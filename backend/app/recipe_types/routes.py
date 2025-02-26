from flask import jsonify, Blueprint

from app.models import RecipeType


recipe_type_bp = Blueprint('recipe_type', __name__)


@recipe_type_bp.route('/')
def list_types():
    types = RecipeType.query.all()

    types_list = [{
        'id': recipe.id,
        'name': recipe.name,
    } for recipe in types]

    return jsonify({'types': types_list})
