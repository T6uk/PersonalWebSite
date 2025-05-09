# Import all models here for easy access
from app.models.user import User
from app.models.player import Player
from app.models.event import Event  # Keep for now
from app.models.game import Game
from app.models.statistics import PlayerStatistics, TeamStatistics
from app.models.trophy import Trophy
# Add new models
from app.models.season import Season
from app.models.competition import Competition
from app.models.league import League
from app.models.tournament import Tournament
from app.models.friendly import Friendly