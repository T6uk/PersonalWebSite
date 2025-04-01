# app/models/Event.py
from datetime import datetime
from ..extensions import db


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(100))
    event_type = db.Column(db.String(50), nullable=False)  # 'league_game', 'tournament', 'friendly_match', 'custom'
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_by = db.relationship('User', backref=db.backref('events_created', lazy=True))

    # Season tracking
    season = db.Column(db.String(20))  # e.g., "2024-2025"

    # Flags for statistics
    has_statistics = db.Column(db.Boolean, default=False)
    statistics_last_updated = db.Column(db.DateTime)

    def __repr__(self):
        return f"Event('{self.title}', '{self.event_type}', '{self.start_datetime}')"

    def get_statistics(self):
        """Return appropriate statistics based on event type"""
        if self.event_type == 'league_game' or self.event_type == 'friendly_match':
            return self.match_statistics.first()
        elif self.event_type == 'tournament':
            return self.tournament_statistics.first()
        return None