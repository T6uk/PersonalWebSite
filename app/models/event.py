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
    opponent = db.Column(db.String(120))
    location = db.Column(db.String(120))
    event_date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text)
    result = db.Column(db.String(20))
    score = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Event {self.title}>'