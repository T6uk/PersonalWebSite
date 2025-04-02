from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from app.config import Config

# Initialize extensions without binding to an app instance
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Add this inside create_app() function
    @app.context_processor
    def inject_year():
        from datetime import datetime
        return {'current_year': datetime.utcnow().year}

    # Import and register blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp)

    from app.core import bp as core_bp
    app.register_blueprint(core_bp)

    from app.players import bp as players_bp
    app.register_blueprint(players_bp)

    from app.matches import bp as matches_bp
    app.register_blueprint(matches_bp)

    from app.stats import bp as stats_bp
    app.register_blueprint(stats_bp)

    # Create initial admin account if it doesn't exist
    with app.app_context():
        # Import models here to avoid circular imports
        from app.models import User, Role
        from app.auth.utils import create_initial_admin
        db.create_all()
        create_initial_admin()

    return app

