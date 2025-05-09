from app.models.competition import Competition
from app import db


class Tournament(Competition):
    __tablename__ = 'tournament'
    id = db.Column(db.Integer, db.ForeignKey('competition.id'), primary_key=True)
    format = db.Column(db.String(64))  # e.g., 'knockout', 'group+knockout'
    num_teams = db.Column(db.Integer)
    current_round = db.Column(db.String(64))

    __mapper_args__ = {
        'polymorphic_identity': 'tournament',
    }

    # Tournament-specific methods
    def get_bracket(self):
        """Return the tournament bracket"""
        # This would be implemented with bracket tracking functionality
        bracket = {}
        return bracket