from app.models.competition import Competition
from app import db


class League(Competition):
    __tablename__ = 'league'
    id = db.Column(db.Integer, db.ForeignKey('competition.id'), primary_key=True)
    format = db.Column(db.String(64))  # e.g., 'round-robin', 'home-away'
    num_teams = db.Column(db.Integer)
    points_for_win = db.Column(db.Integer, default=3)
    points_for_draw = db.Column(db.Integer, default=1)

    __mapper_args__ = {
        'polymorphic_identity': 'league',
    }

    # League-specific methods
    def get_standings(self):
        """Calculate and return league standings"""
        standings = []
        # Implementation to be added
        return standings