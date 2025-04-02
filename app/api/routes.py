from flask import jsonify, request
from flask_login import login_required
from app.api import bp
from app.models import User, Match
from app.utils.decorators import admin_required
import datetime


@bp.route('/matches/upcoming', methods=['GET'])
@login_required
def get_upcoming_matches():
    today = datetime.datetime.now().date()
    upcoming_matches = Match.query.filter(Match.match_date >= today).order_by(Match.match_date).all()

    matches = []
    for match in upcoming_matches:
        matches.append({
            'id': match.id,
            'opponent': match.opponent,
            'date': match.match_date.strftime('%Y-%m-%d %H:%M'),
            'location': match.location,
            'is_home_game': match.is_home_game
        })

    return jsonify({'matches': matches})


@bp.route('/players', methods=['GET'])
@login_required
def get_players():
    players = User.query.filter_by(role='player').all()

    player_list = []
    for player in players:
        player_data = {
            'id': player.id,
            'username': player.username,
            'email': player.email
        }

        if player.player_profile:
            player_data['position'] = player.player_profile.position
            player_data['jersey_number'] = player.player_profile.jersey_number

        player_list.append(player_data)

    return jsonify({'players': player_list})


@bp.route('/users/stats', methods=['GET'])
@login_required
@admin_required
def get_user_stats():
    total_users = User.query.count()
    total_players = User.query.filter_by(role='player').count()
    total_coaches = User.query.filter_by(role='coach').count()
    total_matches = Match.query.count()

    return jsonify({
        'total_users': total_users,
        'total_players': total_players,
        'total_coaches': total_coaches,
        'total_matches': total_matches
    })