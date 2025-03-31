# app/models/event.py
from app.extensions import db
from datetime import datetime


class EventType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    description = db.Column(db.Text)

    # Relationships
    events = db.relationship('Event', backref='event_type', lazy=True)

    def __repr__(self):
        return f'<EventType {self.name}>'


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    event_type_id = db.Column(db.Integer, db.ForeignKey('event_type.id'), nullable=False)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=True)
    opponent = db.Column(db.String(120))
    location = db.Column(db.String(120))
    event_date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text)
    result = db.Column(db.String(20))
    score = db.Column(db.String(20))
    team_score = db.Column(db.Integer, default=0)
    opponent_score = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    game_stats = db.relationship('GamePlayerStat', backref='event', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Event {self.title}>'

    @property
    def formatted_score(self):
        if self.team_score is not None and self.opponent_score is not None:
            return f"{self.team_score} - {self.opponent_score}"
        return self.score