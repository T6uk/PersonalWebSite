# app/models/game_stat.py
from app.extensions import db
from datetime import datetime


class GamePlayerStat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Playing stats
    minutes_played = db.Column(db.Integer, default=0)
    goals = db.Column(db.Integer, default=0)
    assists = db.Column(db.Integer, default=0)
    yellow_cards = db.Column(db.Integer, default=0)
    red_cards = db.Column(db.Integer, default=0)

    # Additional stats
    shots = db.Column(db.Integer, default=0)
    shots_on_target = db.Column(db.Integer, default=0)
    passes = db.Column(db.Integer, default=0)
    pass_accuracy = db.Column(db.Float, default=0)
    tackles = db.Column(db.Integer, default=0)
    fouls_committed = db.Column(db.Integer, default=0)
    fouls_suffered = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    player = db.relationship('User', backref='game_stats')

    def __repr__(self):
        return f'<GamePlayerStat Event: {self.event_id}, Player: {self.player_id}>'