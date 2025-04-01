# app/views/player.py
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models.Event import Event
from datetime import datetime
from functools import wraps

player = Blueprint('player', __name__, url_prefix='/player')


# Decorator to check if user is a player
def player_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_player():
            flash('You need to be a player to access this page.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)

    return decorated_function


@player.route('/dashboard')
@login_required
@player_required
def dashboard():
    # Get upcoming events
    upcoming_events = Event.query.filter(Event.start_datetime > datetime.utcnow()) \
        .order_by(Event.start_datetime).limit(5).all()

    now = datetime.utcnow()

    # Get current season for statistics
    current_year = datetime.utcnow().year
    current_month = datetime.utcnow().month
    if current_month >= 8:  # If after August, use current season format (e.g., 2024-2025)
        current_season = f"{current_year}-{current_year + 1}"
    else:  # If before August, use previous season format
        current_season = f"{current_year - 1}-{current_year}"

    # Get player's season stats
    season_stats = current_user.get_season_statistics(season=current_season)
    recent_performances = current_user.get_recent_performances(limit=3)

    return render_template('player/dashboard.html',
                           title='Player Dashboard',
                           upcoming_events=upcoming_events,
                           now=now,
                           current_season=current_season,
                           season_stats=season_stats,
                           recent_performances=recent_performances)


@player.route('/events')
@login_required
@player_required
def view_events():
    now = datetime.utcnow()

    upcoming_events = Event.query.filter(Event.start_datetime > now) \
        .order_by(Event.start_datetime).all()

    past_events = Event.query.filter(Event.start_datetime <= now) \
        .order_by(Event.start_datetime.desc()).all()

    return render_template('player/events.html', title='Team Events',
                           upcoming_events=upcoming_events, past_events=past_events, now=now)


@player.route('/event/<int:event_id>')
@login_required
@player_required
def view_event(event_id):
    event = Event.query.get_or_404(event_id)
    now = datetime.utcnow()

    # Check if event has statistics
    event_stats = None
    player_stats = None

    if event.has_statistics:
        event_stats = event.get_statistics()

        if event.event_type in ['league_game', 'friendly_match'] and event_stats:
            from ..models.Statistics import PlayerPerformance
            # Get current player's performance in this match
            player_stats = PlayerPerformance.query.filter_by(
                match_id=event_stats.id,
                player_id=current_user.id
            ).first()

    return render_template('player/event_details.html',
                           title=event.title,
                           event=event,
                           now=now,
                           event_stats=event_stats,
                           player_stats=player_stats)


@player.route('/my-statistics')
@login_required
@player_required
def my_statistics():
    # Get current season for statistics
    current_year = datetime.utcnow().year
    current_month = datetime.utcnow().month
    if current_month >= 8:  # If after August, use current season format (e.g., 2024-2025)
        current_season = f"{current_year}-{current_year + 1}"
    else:  # If before August, use previous season format
        current_season = f"{current_year - 1}-{current_year}"

    # Get player's season stats
    season_stats = current_user.get_season_statistics(season=current_season)

    # Get statistics by event type
    league_stats = current_user.get_event_type_statistics('league_game', season=current_season)
    friendly_stats = current_user.get_event_type_statistics('friendly_match', season=current_season)
    tournament_stats = current_user.get_event_type_statistics('tournament', season=current_season)

    # Get recent performances
    recent_performances = current_user.get_recent_performances(limit=10)

    return render_template('player/my_statistics.html',
                           title='My Statistics',
                           current_season=current_season,
                           season_stats=season_stats,
                           league_stats=league_stats,
                           friendly_stats=friendly_stats,
                           tournament_stats=tournament_stats,
                           recent_performances=recent_performances)