# app/models/User.py
from datetime import datetime
from flask_login import UserMixin
from ..extensions import db, bcrypt
from sqlalchemy import and_, func


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

    # Player statistics methods
    def get_season_statistics(self, season=None):
        """Get player statistics for a specific season"""
        from ..models.Statistics import PlayerPerformance, MatchStatistic
        from ..models.Event import Event

        # Define base query to get all player performances
        query = db.session.query(
            func.count(PlayerPerformance.id).label('matches_played'),
            func.sum(PlayerPerformance.minutes_played).label('total_minutes'),
            func.sum(PlayerPerformance.goals).label('total_goals'),
            func.sum(PlayerPerformance.assists).label('total_assists'),
            func.sum(PlayerPerformance.yellow_cards).label('total_yellows'),
            func.sum(PlayerPerformance.red_cards).label('total_reds'),
            func.avg(PlayerPerformance.rating).label('avg_rating')
        ).join(
            MatchStatistic, MatchStatistic.id == PlayerPerformance.match_id
        ).join(
            Event, Event.id == MatchStatistic.event_id
        ).filter(
            PlayerPerformance.player_id == self.id
        )

        # Apply season filter if provided
        if season:
            query = query.filter(Event.season == season)

        return query.first()

    def get_event_type_statistics(self, event_type, season=None):
        """Get player statistics for a specific event type (league_game, friendly_match)"""
        from ..models.Statistics import PlayerPerformance, MatchStatistic
        from ..models.Event import Event

        # Define base query to get player performances for specified event type
        query = db.session.query(
            func.count(PlayerPerformance.id).label('matches_played'),
            func.sum(PlayerPerformance.minutes_played).label('total_minutes'),
            func.sum(PlayerPerformance.goals).label('total_goals'),
            func.sum(PlayerPerformance.assists).label('total_assists'),
            func.sum(PlayerPerformance.yellow_cards).label('total_yellows'),
            func.sum(PlayerPerformance.red_cards).label('total_reds'),
            func.avg(PlayerPerformance.rating).label('avg_rating')
        ).join(
            MatchStatistic, MatchStatistic.id == PlayerPerformance.match_id
        ).join(
            Event, Event.id == MatchStatistic.event_id
        ).filter(
            PlayerPerformance.player_id == self.id,
            Event.event_type == event_type
        )

        # Apply season filter if provided
        if season:
            query = query.filter(Event.season == season)

        return query.first()

    def get_tournament_statistics(self, tournament_id=None, season=None):
        """Get player's tournament statistics"""
        from ..models.Statistics import PlayerPerformance, MatchStatistic, TournamentMatch, TournamentStatistic
        from ..models.Event import Event

        # Define base query for tournament performances
        query = db.session.query(
            func.count(PlayerPerformance.id).label('matches_played'),
            func.sum(PlayerPerformance.goals).label('total_goals'),
            func.sum(PlayerPerformance.assists).label('total_assists'),
            func.avg(PlayerPerformance.rating).label('avg_rating')
        ).join(
            MatchStatistic, MatchStatistic.id == PlayerPerformance.match_id
        ).join(
            Event, Event.id == MatchStatistic.event_id
        ).filter(
            PlayerPerformance.player_id == self.id,
            Event.event_type == 'tournament'
        )

        # Filter by specific tournament if provided
        if tournament_id:
            tournament_events = db.session.query(TournamentStatistic.event_id).filter(
                TournamentStatistic.id == tournament_id
            ).subquery()

            query = query.filter(Event.id.in_(tournament_events))

        # Apply season filter if provided
        if season:
            query = query.filter(Event.season == season)

        return query.first()

    def get_recent_performances(self, limit=5):
        """Get player's most recent performances"""
        from ..models.Statistics import PlayerPerformance, MatchStatistic

        return PlayerPerformance.query.join(
            MatchStatistic, MatchStatistic.id == PlayerPerformance.match_id
        ).filter(
            PlayerPerformance.player_id == self.id
        ).order_by(
            MatchStatistic.match_date.desc()
        ).limit(limit).all()