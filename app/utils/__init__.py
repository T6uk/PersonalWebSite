# Import utility functions and classes
from app.utils.jinja_filters import register_filters

def init_app(app):
    """Initialize app with utility functions"""
    register_filters(app)