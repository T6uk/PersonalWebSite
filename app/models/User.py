from datetime import datetime
from flask_login import UserMixin
from ..extensions import db, bcrypt


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='player')  # 'admin' or 'player'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Player-specific fields
    position = db.Column(db.String(50))
    jersey_number = db.Column(db.Integer)
    date_of_birth = db.Column(db.Date)
    height = db.Column(db.Float)  # in cm
    weight = db.Column(db.Float)  # in kg
    bio = db.Column(db.Text)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def is_player(self):
        return self.role == 'player'

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.role}')"