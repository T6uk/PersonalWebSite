# app/views/main.py
from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required
from ..models.Event import Event
from ..models.User import User
from ..models.Statistics import PlayerPerformance, MatchStatistic
from ..extensions import db
from datetime import datetime
from sqlalchemy import func, desc

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('player.dashboard'))

    # Get the current date for filtering events
    now = datetime.utcnow()

    # Get upcoming events
    upcoming_events = Event.query.filter(Event.start_datetime > now) \
        .order_by(Event.start_datetime) \
        .limit(5).all()

    # Get past events
    past_events = Event.query.filter(Event.start_datetime <= now) \
        .order_by(desc(Event.start_datetime)) \
        .limit(5).all()

    # Get top performing players
    # This query gets players with most goals in recent matches
    top_scorers = db.session.query(
        User,
        func.sum(PlayerPerformance.goals).label('total_goals'),
        func.sum(PlayerPerformance.assists).label('total_assists'),
        func.avg(PlayerPerformance.rating).label('avg_rating')
    ).join(
        PlayerPerformance, User.id == PlayerPerformance.player_id
    ).filter(
        User.role == 'player'
    ).group_by(
        User.id
    ).order_by(
        desc('total_goals'),
        desc('total_assists')
    ).limit(5).all()

    # Format the results for template
    formatted_top_scorers = []
    for player, goals, assists, rating in top_scorers:
        formatted_top_scorers.append({
            'username': player.username,
            'position': player.position,
            'jersey_number': player.jersey_number,
            'total_goals': goals,
            'total_assists': assists,
            'avg_rating': rating
        })

    return render_template('home.html',
                           title='Welcome to FC Mara',
                           upcoming_events=upcoming_events,
                           past_events=past_events,
                           top_scorers=formatted_top_scorers,
                           now=now)


@main.route('/home')
@login_required
def home():
    return render_template('home.html', title='Home')