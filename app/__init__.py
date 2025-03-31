# app/__init__.py
from flask import Flask
from config import Config
from app.extensions import db, migrate, login_manager, bcrypt, mail
import os
import logging
from logging.handlers import RotatingFileHandler
from flask.cli import with_appcontext
import click
from app import filters
from app.context_processors import utility_processor


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)

    # Configure login
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # Initialize filters and context processors
    filters.init_app(app)
    app.context_processor(utility_processor)

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register blueprints
    from app.auth.routes import auth
    from app.admin.routes import admin
    from app.players.routes import players
    from app.events.routes import events
    from app.statistics.routes import statistics
    from app.trophies.routes import trophies
    from app.errors import errors

    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(players, url_prefix='/players')
    app.register_blueprint(events, url_prefix='/events')
    app.register_blueprint(statistics, url_prefix='/statistics')
    app.register_blueprint(trophies, url_prefix='/trophies')
    app.register_blueprint(errors)

    # Main route
    from flask import render_template

    @app.route('/')
    def index():
        return render_template('index.html')

    # Setup logging
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/football_team_management.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Football Team Management startup')

    return app


def create_admin_user():
    """Create initial admin user if none exists."""
    from app.models.user import User
    from app.extensions import db

    # Check if any admin exists
    admin_exists = User.query.filter_by(user_type='admin').first()
    if admin_exists:
        return

    # Create admin user
    admin = User(
        username='admin',
        email='admin@example.com',
        first_name='Admin',
        last_name='User',
        user_type='admin'
    )
    admin.set_password('admin123')  # This should be changed immediately

    db.session.add(admin)
    db.session.commit()

    print('Created admin user: admin@example.com / admin123')
    print('Please change this password immediately after first login')


def init_event_types():
    """Initialize default event types if they don't exist."""
    from app.models.event import EventType
    from app.extensions import db

    # Default event types
    event_types = [
        {'name': 'Tournament', 'description': 'A tournament consisting of multiple games'},
        {'name': 'League Match', 'description': 'Regular league match'},
        {'name': 'Cup Match', 'description': 'Cup competition match'},
        {'name': 'Friendly', 'description': 'Friendly match'},
        {'name': 'Training', 'description': 'Team training session'}
    ]

    # Check and create event types
    for et in event_types:
        existing = EventType.query.filter_by(name=et['name']).first()
        if not existing:
            event_type = EventType(name=et['name'], description=et['description'])
            db.session.add(event_type)

    db.session.commit()
    print('Event types initialized')
