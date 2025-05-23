# app/models/game.py
from app import db
from datetime import datetime
from sqlalchemy.orm import relationship


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Support both old and new systems during transition
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    competition_id = db.Column(db.Integer, db.ForeignKey('competition.id'))

    opponent = db.Column(db.String(128), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(128))
    is_home_game = db.Column(db.Boolean, default=True)
    score_team = db.Column(db.Integer)
    score_opponent = db.Column(db.Integer)
    status = db.Column(db.String(32), default='upcoming')  # 'upcoming', 'completed', 'cancelled'
    highlights_url = db.Column(db.String(256))
    notes = db.Column(db.Text)

    # Competition-specific fields
    round = db.Column(db.String(64))  # For tournaments (e.g., 'group', 'quarter-final')
    matchday = db.Column(db.Integer)  # For leagues (e.g., matchday number)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    event = relationship("Event", back_populates="games", foreign_keys=[event_id])
    competition = relationship("Competition", back_populates="games", foreign_keys=[competition_id])
    player_statistics = relationship("PlayerStatistics", back_populates="game", cascade="all, delete-orphan")

    @property
    def result(self):
        """Return the result of the game (win, loss, draw)"""
        if self.status != 'completed' or self.score_team is None or self.score_opponent is None:
            return None

        if self.score_team > self.score_opponent:
            return 'win'
        elif self.score_team < self.score_opponent:
            return 'loss'
        else:
            return 'draw'

    @property
    def score_display(self):
        """Return a formatted score string"""
        if self.status != 'completed' or self.score_team is None or self.score_opponent is None:
            return 'vs'

        return f"{self.score_team} - {self.score_opponent}"

    def __repr__(self):
        return f'<Game vs {self.opponent} on {self.date.strftime("%Y-%m-%d")}>'