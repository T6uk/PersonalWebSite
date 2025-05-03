from app import db
from datetime import datetime
from sqlalchemy.orm import relationship


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    position = db.Column(db.String(64), nullable=False)
    jersey_number = db.Column(db.Integer)
    date_of_birth = db.Column(db.Date)
    height = db.Column(db.Float)  # in cm
    weight = db.Column(db.Float)  # in kg
    nationality = db.Column(db.String(64))
    bio = db.Column(db.Text)
    image_url = db.Column(db.String(256))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    statistics = relationship("PlayerStatistics", back_populates="player", cascade="all, delete-orphan")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_total_statistics(self):
        """Get aggregated statistics for this player across all games"""
        total_stats = {
            'appearances': 0,
            'goals': 0,
            'assists': 0,
            'yellow_cards': 0,
            'red_cards': 0,
            'minutes_played': 0
        }

        for stat in self.statistics:
            total_stats['appearances'] += 1
            total_stats['goals'] += stat.goals
            total_stats['assists'] += stat.assists
            total_stats['yellow_cards'] += stat.yellow_cards
            total_stats['red_cards'] += stat.red_cards
            total_stats['minutes_played'] += stat.minutes_played

        return total_stats

    def __repr__(self):
        return f'<Player {self.full_name}>'