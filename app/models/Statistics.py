# app/models/Statistics.py
from datetime import datetime
from ..extensions import db


class MatchStatistic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    event = db.relationship('Event', backref=db.backref('match_statistics', cascade='all, delete-orphan'))

    # Match details
    home_team = db.Column(db.String(100), nullable=False, default='FC Mara')
    away_team = db.Column(db.String(100), nullable=False)
    home_score = db.Column(db.Integer, default=0)
    away_score = db.Column(db.Integer, default=0)
    match_date = db.Column(db.DateTime, nullable=False)

    # Additional match information
    location = db.Column(db.String(100))
    referee = db.Column(db.String(100))
    attendance = db.Column(db.Integer)
    notes = db.Column(db.Text)

    # Creation metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_by = db.relationship('User', foreign_keys=[created_by_id])

    def __repr__(self):
        return f"MatchStatistic('{self.home_team}' vs '{self.away_team}', {self.home_score}-{self.away_score})"


class PlayerPerformance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match_statistic.id'), nullable=False)
    match = db.relationship('MatchStatistic', backref=db.backref('player_performances', cascade='all, delete-orphan'))
    player_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    player = db.relationship('User', backref=db.backref('performances', lazy=True))

    # Basic performance stats
    minutes_played = db.Column(db.Integer, default=0)
    goals = db.Column(db.Integer, default=0)
    assists = db.Column(db.Integer, default=0)
    yellow_cards = db.Column(db.Integer, default=0)
    red_cards = db.Column(db.Integer, default=0)

    # Additional player stats based on position
    # All positions
    passes_completed = db.Column(db.Integer, default=0)
    pass_accuracy = db.Column(db.Float, default=0.0)  # percentage

    # Offensive players
    shots = db.Column(db.Integer, default=0)
    shots_on_target = db.Column(db.Integer, default=0)
    dribbles_completed = db.Column(db.Integer, default=0)

    # Midfielders
    tackles = db.Column(db.Integer, default=0)
    interceptions = db.Column(db.Integer, default=0)

    # Defenders
    clearances = db.Column(db.Integer, default=0)
    blocks = db.Column(db.Integer, default=0)

    # Goalkeepers
    saves = db.Column(db.Integer, default=0)
    goals_conceded = db.Column(db.Integer, default=0)

    # Player rating
    rating = db.Column(db.Float, default=0.0)  # 1-10 scale

    # Notes
    notes = db.Column(db.Text)

    # Creation metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"PlayerPerformance(Player: {self.player.username}, Goals: {self.goals}, Assists: {self.assists})"


class TournamentStatistic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    event = db.relationship('Event', backref=db.backref('tournament_statistics', cascade='all, delete-orphan'))

    # Tournament details
    tournament_name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)

    # Team performance
    position = db.Column(db.Integer)  # Final standing
    matches_played = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    draws = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    goals_for = db.Column(db.Integer, default=0)
    goals_against = db.Column(db.Integer, default=0)

    # Additional tournament information
    location = db.Column(db.String(100))
    notes = db.Column(db.Text)

    # Creation metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_by = db.relationship('User', foreign_keys=[created_by_id])

    def __repr__(self):
        return f"TournamentStatistic('{self.tournament_name}', Position: {self.position})"


class TournamentMatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament_statistic.id'), nullable=False)
    tournament = db.relationship('TournamentStatistic', backref=db.backref('matches', cascade='all, delete-orphan'))

    # Match details
    match_round = db.Column(db.String(50))  # Group Stage, Quarterfinal, Semifinal, Final, etc.
    home_team = db.Column(db.String(100), nullable=False)
    away_team = db.Column(db.String(100), nullable=False)
    home_score = db.Column(db.Integer, default=0)
    away_score = db.Column(db.Integer, default=0)
    match_date = db.Column(db.DateTime, nullable=False)

    # Additional match information
    location = db.Column(db.String(100))
    notes = db.Column(db.Text)

    # Creation metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"TournamentMatch('{self.home_team}' vs '{self.away_team}', {self.match_round})"