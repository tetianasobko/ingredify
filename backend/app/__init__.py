from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect


db = SQLAlchemy()
migrate = Migrate()
# csrf = CSRFProtect()


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object('app.config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    # csrf.init_app(app)
    CORS(
        app,
        resources={r"/api/*": {"origins": "http://localhost:5173"}},
        supports_credentials=True
    )

    from app.recipes.routes import recipe_bp
    from app.ingredients.routes import ingredient_bp
    from app.recipe_types.routes import recipe_type_bp

    app.register_blueprint(recipe_bp, url_prefix='/api/recipes')
    app.register_blueprint(ingredient_bp, url_prefix='/api/ingredients')
    app.register_blueprint(recipe_type_bp, url_prefix='/api/types')

    return app
