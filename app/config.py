import os
from datetime import timedelta


class Config:
    # Secret key for sessions and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret_key_change_in_production')

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///football_team.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload folder for player images, etc.
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload

    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)

    # Security settings
    SESSION_COOKIE_SECURE = os.environ.get('PRODUCTION', 'False') == 'True'
    REMEMBER_COOKIE_SECURE = os.environ.get('PRODUCTION', 'False') == 'True'