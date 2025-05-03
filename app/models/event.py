from app import db
from datetime import datetime
from sqlalchemy.orm import relationship


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    event_type = db.Column(db.String(32), nullable=False)  # 'league', 'tournament', 'friendly'
    season = db.Column(db.String(32), nullable=False)  # e.g. '2024-2025'
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    location = db.Column(db.String(128))
    description = db.Column(db.Text)
    image_url = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    games = relationship("Game", back_populates="event", cascade="all, delete-orphan")

    def is_active(self):
        """Check if the event is currently active"""
        now = datetime.now().date()
        if self.end_date:
            return self.start_date <= now <= self.end_date
        return self.start_date <= now

    def get_status(self):
        """Get the status of the event (upcoming, active, completed)"""
        now = datetime.now().date()

        if now < self.start_date:
            return "upcoming"
        elif self.end_date and now > self.end_date:
            return "completed"
        else:
            return "active"

    def __repr__(self):
        return f'<Event {self.name} ({self.event_type})>'