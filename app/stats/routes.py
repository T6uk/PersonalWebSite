# app/stats/routes.py
from flask import render_template
from flask_login import login_required
from app import db
from app.stats import bp
from app.models import Match, User, PlayerProfile, Goal, Card
import datetime
import json  # Add this import


@bp.route('/dashboard')
@login_required
def dashboard():
    # Get match statistics
    total_matches = Match.query.count()

    # Get past matches with results
    today = datetime.datetime.now().date()
    past_matches = Match.query.filter(Match.match_date < today).all()

    # Calculate match results
    wins = 0
    draws = 0
    losses = 0
    goals_scored = 0
    goals_conceded = 0

    for match in past_matches:
        if match.score_team is not None and match.score_opponent is not None:
            goals_scored += match.score_team
            goals_conceded += match.score_opponent

            if match.score_team > match.score_opponent:
                wins += 1
            elif match.score_team == match.score_opponent:
                draws += 1
            else:
                losses += 1

    # Get player statistics
    total_players = User.query.filter_by(role='player').count()

    # Get positions breakdown
    goalkeeper_count = PlayerProfile.query.filter_by(position='goalkeeper').count()
    defender_count = PlayerProfile.query.filter_by(position='defender').count()
    midfielder_count = PlayerProfile.query.filter_by(position='midfielder').count()
    forward_count = PlayerProfile.query.filter_by(position='forward').count()

    # Prepare data for charts
    position_data = {
        'labels': json.dumps(['Goalkeepers', 'Defenders', 'Midfielders', 'Forwards']),
        'values': json.dumps([goalkeeper_count, defender_count, midfielder_count, forward_count])
    }

    results_data = {
        'labels': json.dumps(['Wins', 'Draws', 'Losses']),
        'values': json.dumps([wins, draws, losses])
    }

    # Calculate team performance percentage - Fix here
    total_games_with_result = wins + draws + losses
    win_percentage = round((wins / total_games_with_result * 100) if total_games_with_result > 0 else 0, 1)

    upcoming_matches = Match.query.filter(Match.match_date >= today).order_by(Match.match_date).limit(3).all()
    recent_matches = Match.query.filter(Match.match_date < today).order_by(Match.match_date.desc()).limit(3).all()

    # Get player stats for top performers
    top_scorers = db.session.query(
        User, db.func.count(Goal.id).label('goals')
    ).join(Goal, User.id == Goal.player_id).group_by(User.id).order_by(db.desc('goals')).limit(5).all()

    recent_goals = db.session.query(
        User, Goal, Match
    ).join(Goal, User.id == Goal.player_id).join(Match, Goal.match_id == Match.id).order_by(
        Goal.created_at.desc()).limit(10).all()

    yellow_cards = db.session.query(
        User, db.func.count(Card.id).label('cards')
    ).join(Card, User.id == Card.player_id).filter(Card.card_type == 'yellow').group_by(User.id).order_by(
        db.desc('cards')).limit(5).all()

    red_cards = db.session.query(
        User, db.func.count(Card.id).label('cards')
    ).join(Card, User.id == Card.player_id).filter(Card.card_type == 'red').group_by(User.id).order_by(
        db.desc('cards')).limit(5).all()

    return render_template('stats/dashboard.html',
                           title='Team Statistics',
                           total_matches=total_matches,
                           wins=wins,
                           draws=draws,
                           losses=losses,
                           goals_scored=goals_scored,
                           goals_conceded=goals_conceded,
                           total_players=total_players,
                           position_data=position_data,
                           results_data=results_data,
                           win_percentage=win_percentage,
                           upcoming_matches=upcoming_matches,
                           recent_matches=recent_matches,
                           top_scorers=top_scorers,
                           recent_goals=recent_goals,
                           yellow_cards=yellow_cards,
                           red_cards=red_cards)