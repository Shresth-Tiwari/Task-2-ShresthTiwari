from flask import Flask
from config import config
from app.extensions import db, migrate, cors


def create_app(config_name="default"):
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)

    # Register blueprints
    from app.routes import users_bp
    app.register_blueprint(users_bp, url_prefix="/api")

    # Health check route
    @app.route("/")
    def index():
        return {"message": "Flask + PostgreSQL API is running!", "status": "ok"}

    return app
