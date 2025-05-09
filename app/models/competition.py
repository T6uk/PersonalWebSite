from app import db
from datetime import datetime
from sqlalchemy.orm import relationship


class Competition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    season_id = db.Column(db.Integer, db.ForeignKey('season.id'), nullable=False)
    competition_type = db.Column(db.String(32), nullable=False)  # 'league', 'tournament', 'friendly'
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    location = db.Column(db.String(128))
    description = db.Column(db.Text)
    image_url = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Add table inheritance
    __mapper_args__ = {
        'polymorphic_on': competition_type,
        'polymorphic_identity': 'competition'
    }

    # Relationships
    season = relationship("Season", back_populates="competitions")
    games = relationship("Game", back_populates="competition", foreign_keys="Game.competition_id", cascade="all, delete-orphan")

    def is_active(self):
        """Check if the competition is currently active"""
        now = datetime.now().date()
        if self.end_date:
            return self.start_date <= now <= self.end_date
        return self.start_date <= now

    def get_status(self):
        """Get the status of the competition (upcoming, active, completed)"""
        now = datetime.now().date()

        if now < self.start_date:
            return "upcoming"
        elif self.end_date and now > self.end_date:
            return "completed"
        else:
            return "active"

    def __repr__(self):
        return f'<Competition {self.name} ({self.competition_type})>'