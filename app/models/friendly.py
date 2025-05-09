from app.models.competition import Competition
from app import db


class Friendly(Competition):
    __tablename__ = 'friendly'
    id = db.Column(db.Integer, db.ForeignKey('competition.id'), primary_key=True)
    purpose = db.Column(db.String(128))  # e.g., 'Pre-season', 'Charity'

    __mapper_args__ = {
        'polymorphic_identity': 'friendly',
    }