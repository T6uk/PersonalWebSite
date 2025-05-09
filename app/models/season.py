from app import db
from datetime import datetime
from sqlalchemy.orm import relationship

class Season(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)  # e.g., '2024-2025'
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    is_current = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    competitions = relationship("Competition", back_populates="season", cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Season {self.name}>'