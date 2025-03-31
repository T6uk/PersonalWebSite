from app.extensions import db, login_manager, bcrypt
from flask_login import UserMixin
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    user_type = db.Column(db.String(20), nullable=False, default='player')
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    profile_picture = db.Column(db.String(120), default='default.jpg')
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    player_stats = db.relationship('PlayerStatistic', backref='player', lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.user_type == 'admin'

    def is_player(self):
        return self.user_type == 'player'

    def __repr__(self):
        return f'<User {self.username}>'

    def get_reset_token(self):
        from app.utils.email import generate_reset_token
        return generate_reset_token(self.email)

    @staticmethod
    def verify_reset_token(token):
        from app.utils.email import verify_reset_token
        return verify_reset_token(token)
