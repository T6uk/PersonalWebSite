from flask import Blueprint

bp = Blueprint('players', __name__, url_prefix='/players')

from app.players import routes
