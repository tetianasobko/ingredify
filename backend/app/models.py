from app import db

# --- ASSOCIATION TABLE ---
recipe_type_association = db.Table(
    'recipe_type_association',
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id'),
              primary_key=True),
    db.Column('type_id', db.Integer, db.ForeignKey('recipe_type.id'),
              primary_key=True)
)


# --- RECIPE MODELS ---
class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    source = db.Column(db.String(500))  # URL or text reference
    steps = db.Column(db.Text, nullable=False)

    ingredients = db.relationship('RecipeIngredient', back_populates='recipe',
                                  cascade="all, delete-orphan")
    types = db.relationship('RecipeType', secondary=recipe_type_association,
                            back_populates='recipes')


class RecipeType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    recipes = db.relationship('Recipe', secondary=recipe_type_association,
                              back_populates='types')


# --- INGREDIENT MODELS ---
class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer,
                            db.ForeignKey('ingredient_category.id'),
                            nullable=True)

    category = db.relationship('IngredientCategory', backref='ingredients')
    recipes = db.relationship('RecipeIngredient', back_populates='ingredient',
                              cascade="all, delete-orphan")


class IngredientCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)


# --- MANY-TO-MANY RELATIONSHIP MODEL ---
class RecipeIngredient(db.Model):
    """
    Many-to-Many relationship between Recipe and Ingredient.
    Stores amount and unit for each ingredient.
    """
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'),
                          nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'),
                              nullable=False)
    amount = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50))

    recipe = db.relationship('Recipe', back_populates='ingredients')
    ingredient = db.relationship('Ingredient', back_populates='recipes')
