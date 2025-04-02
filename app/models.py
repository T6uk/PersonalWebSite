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


class MatchType:
    FRIENDLY = 'friendly'
    LEAGUE = 'league'
    TOURNAMENT = 'tournament'
    CUP = 'cup'


class CardType:
    YELLOW = 'yellow'
    RED = 'red'


class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    minute = db.Column(db.Integer, nullable=False)
    is_own_goal = db.Column(db.Boolean, default=False)
    is_penalty = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    player = db.relationship('User')

    def __repr__(self):
        return f'<Goal by {self.player.username} at {self.minute}>'


class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    card_type = db.Column(db.String(10), nullable=False)
    minute = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    player = db.relationship('User')

    def __repr__(self):
        return f'<{self.card_type.capitalize()} Card for {self.player.username} at {self.minute}>'


class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    opponent = db.Column(db.String(100), nullable=False)
    match_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    is_home_game = db.Column(db.Boolean, default=True)
    match_type = db.Column(db.String(20), default=MatchType.FRIENDLY)
    tournament_name = db.Column(db.String(100), nullable=True)
    score_team = db.Column(db.Integer, nullable=True)
    score_opponent = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    goals = db.relationship('Goal', backref='match', lazy='dynamic', cascade='all, delete-orphan')
    cards = db.relationship('Card', backref='match', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Match vs {self.opponent} on {self.match_date}>'