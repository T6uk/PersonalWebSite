from flask import current_app
from app.models.event import Event
from app.models.statistic import TeamStatistic
from app.models.trophy import Trophy
from datetime import datetime


def utility_processor():
    """Context processor to make functions available in templates."""

    def get_upcoming_events(limit=3):
        """Get upcoming events."""
        now = datetime.utcnow()
        return Event.query.filter(Event.event_date > now).order_by(Event.event_date).limit(limit).all()

    def get_latest_team_stats():
        """Get latest team statistics."""
        return TeamStatistic.query.order_by(TeamStatistic.season.desc()).first()

    def get_recent_trophies(limit=3):
        """Get recent trophies."""
        return Trophy.query.order_by(Trophy.year.desc()).limit(limit).all()

    def get_recent_events(limit=5):
        """Get recent events."""
        return Event.query.order_by(Event.created_at.desc()).limit(limit).all()

    def get_related_trophies(year, current_id, limit=3):
        """Get related trophies from the same year, excluding current trophy."""
        from app.models.trophy import Trophy
        return Trophy.query.filter(Trophy.year == year, Trophy.id != current_id).limit(limit).all()

    def now(format='%Y'):
        """Get current date/time in specified format."""
        return datetime.utcnow().strftime(format)

    return dict(
        get_upcoming_events=get_upcoming_events,
        get_latest_team_stats=get_latest_team_stats,
        get_recent_trophies=get_recent_trophies,
        get_recent_events=get_recent_events,
        get_related_trophies=get_related_trophies,
        now=now
    )