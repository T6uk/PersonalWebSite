from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


class Role:
    ADMIN = 'admin'
    PLAYER = 'player'
    COACH = 'coach'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False, default=Role.PLAYER)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships - to be implemented when extending
    player_profile = db.relationship('PlayerProfile', backref='user', uselist=False, lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == Role.ADMIN

    def is_player(self):
        return self.role == Role.PLAYER

    def is_coach(self):
        return self.role == Role.COACH


class PlayerProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    position = db.Column(db.String(20), default='midfielder')
    jersey_number = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)  # in cm
    weight = db.Column(db.Integer, nullable=True)  # in kg
    date_of_birth = db.Column(db.Date, nullable=True)
    dominant_foot = db.Column(db.String(10), nullable=True)
    bio = db.Column(db.Text, nullable=True)

    # Remove this line as we already defined the relationship in User model
    # user = db.relationship('User', backref='player_profile', uselist=False)

    def __repr__(self):
        return f'<PlayerProfile {self.user.username}>'


class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    opponent = db.Column(db.String(100), nullable=False)
    match_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    is_home_game = db.Column(db.Boolean, default=True)
    score_team = db.Column(db.Integer, nullable=True)
    score_opponent = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Match vs {self.opponent} on {self.match_date}>'