from flask import Blueprint

bp = Blueprint('stats', __name__, url_prefix='/stats')

from app.stats import routes