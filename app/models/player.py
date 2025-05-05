# Fixed Player Model to prevent recursion
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

    # Career statistics (prior to joining the team)
    career_appearances = db.Column(db.Integer, default=0)
    career_goals = db.Column(db.Integer, default=0)
    career_assists = db.Column(db.Integer, default=0)
    career_yellow_cards = db.Column(db.Integer, default=0)
    career_red_cards = db.Column(db.Integer, default=0)
    career_minutes_played = db.Column(db.Integer, default=0)

    # Relationships
    statistics = relationship("PlayerStatistics", back_populates="player", cascade="all, delete-orphan")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_team_statistics(self):
        """Get statistics for this player from team games only"""
        team_stats = {
            'appearances': 0,
            'goals': 0,
            'assists': 0,
            'yellow_cards': 0,
            'red_cards': 0,
            'minutes_played': 0
        }

        for stat in self.statistics:
            team_stats['appearances'] += 1
            team_stats['goals'] += stat.goals
            team_stats['assists'] += stat.assists
            team_stats['yellow_cards'] += stat.yellow_cards
            team_stats['red_cards'] += stat.red_cards
            team_stats['minutes_played'] += stat.minutes_played

        return team_stats

    def get_career_statistics(self):
        """Get career statistics for this player (prior to joining the team)"""
        return {
            'appearances': self.career_appearances or 0,
            'goals': self.career_goals or 0,
            'assists': self.career_assists or 0,
            'yellow_cards': self.career_yellow_cards or 0,
            'red_cards': self.career_red_cards or 0,
            'minutes_played': self.career_minutes_played or 0
        }

    def get_total_statistics(self):
        """Get aggregated statistics for this player across all games + career stats"""
        # Get team stats first
        team_stats = self.get_team_statistics()
        career_stats = self.get_career_statistics()

        # Create a new dictionary for total stats
        total_stats = {
            'appearances': team_stats['appearances'] + career_stats['appearances'],
            'goals': team_stats['goals'] + career_stats['goals'],
            'assists': team_stats['assists'] + career_stats['assists'],
            'yellow_cards': team_stats['yellow_cards'] + career_stats['yellow_cards'],
            'red_cards': team_stats['red_cards'] + career_stats['red_cards'],
            'minutes_played': team_stats['minutes_played'] + career_stats['minutes_played']
        }

        return total_stats

    def __repr__(self):
        return f'<Player {self.full_name}>'