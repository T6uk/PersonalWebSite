from app import db
from datetime import datetime
from sqlalchemy.orm import relationship


class PlayerStatistics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)

    # Performance stats
    goals = db.Column(db.Integer, default=0)
    assists = db.Column(db.Integer, default=0)
    minutes_played = db.Column(db.Integer, default=0)

    # Disciplinary stats
    yellow_cards = db.Column(db.Integer, default=0)
    red_cards = db.Column(db.Integer, default=0)

    # Additional stats for more detailed analysis
    shots = db.Column(db.Integer, default=0)
    shots_on_target = db.Column(db.Integer, default=0)
    passes = db.Column(db.Integer, default=0)
    pass_accuracy = db.Column(db.Float, default=0)  # percentage
    tackles = db.Column(db.Integer, default=0)
    interceptions = db.Column(db.Integer, default=0)
    fouls_committed = db.Column(db.Integer, default=0)
    fouls_drawn = db.Column(db.Integer, default=0)

    rating = db.Column(db.Float)  # Player rating for the game (e.g., 1-10)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    player = relationship("Player", back_populates="statistics")
    game = relationship("Game", back_populates="player_statistics")

    def __repr__(self):
        return f'<PlayerStatistics for {self.player.full_name} in game {self.game_id}>'


class TeamStatistics:
    """Helper class to calculate team statistics across games"""

    @staticmethod
    def get_season_stats(season=None):
        """Get aggregated team statistics for a season"""
        from app.models.game import Game
        from app.models.event import Event

        query = db.session.query(Game).join(Event)

        if season:
            query = query.filter(Event.season == season)

        games = query.filter(Game.status == 'completed').all()

        stats = {
            'total_games': len(games),
            'wins': 0,
            'draws': 0,
            'losses': 0,
            'goals_for': 0,
            'goals_against': 0,
            'clean_sheets': 0,
            'home_wins': 0,
            'away_wins': 0
        }

        for game in games:
            # Count results
            if game.result == 'win':
                stats['wins'] += 1
                if game.is_home_game:
                    stats['home_wins'] += 1
                else:
                    stats['away_wins'] += 1
            elif game.result == 'draw':
                stats['draws'] += 1
            elif game.result == 'loss':
                stats['losses'] += 1

            # Count goals
            stats['goals_for'] += game.score_team or 0
            stats['goals_against'] += game.score_opponent or 0

            # Count clean sheets
            if game.score_opponent == 0:
                stats['clean_sheets'] += 1

        # Calculate additional stats
        stats['points'] = (stats['wins'] * 3) + stats['draws']
        stats['win_percentage'] = (stats['wins'] / stats['total_games'] * 100) if stats['total_games'] > 0 else 0
        stats['goal_difference'] = stats['goals_for'] - stats['goals_against']

        return stats

    @staticmethod
    def get_top_scorers(limit=5, season=None):
        """Get top scorers for a season or all-time"""
        from app.models.player import Player
        from app.models.game import Game
        from app.models.event import Event

        query = db.session.query(
            Player,
            db.func.sum(PlayerStatistics.goals).label('total_goals')
        ).join(
            PlayerStatistics, Player.id == PlayerStatistics.player_id
        ).join(
            Game, PlayerStatistics.game_id == Game.id
        ).join(
            Event, Game.event_id == Event.id
        ).group_by(
            Player.id
        ).order_by(
            db.desc('total_goals')
        )

        if season:
            query = query.filter(Event.season == season)

        return query.limit(limit).all()