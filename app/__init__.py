from flask import Flask
from .config import Config
from .extensions import db, login_manager, bcrypt, migrate
import os


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    # Set up login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # Import models (must be after db initialization but before create_all)
    from .models.User import User
    from .models.Event import Event
    from .models.Statistics import MatchStatistic, PlayerPerformance, TournamentStatistic, TournamentMatch

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from .views.main import main
    from .views.auth import auth
    from .views.admin import admin
    from .views.admin_statistics import admin_stats
    from .views.player import player

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(admin_stats)
    app.register_blueprint(player)

    # Create database
    with app.app_context():
        db.create_all()

        # Create admin user if not exists
        admin_exists = User.query.filter_by(username='admin').first()
        if not admin_exists:
            admin_user = User(
                username='admin',
                email='admin@example.com',
                role='admin'
            )
            admin_user.set_password('1234')
            db.session.add(admin_user)
            db.session.commit()

    return app