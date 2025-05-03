from flask import Blueprint, render_template, request, current_app
from app.models.player import Player
from app.models.event import Event
from app.models.game import Game
from app.models.statistics import PlayerStatistics, TeamStatistics
from app.models.trophy import Trophy
from sqlalchemy import desc, func
from datetime import datetime
from app import db

public = Blueprint('public', __name__)


@public.route('/')
def index():
    # Get upcoming events
    upcoming_events = Event.query.filter(Event.start_date >= datetime.now().date()).order_by(Event.start_date).limit(
        3).all()

    # Get upcoming games
    upcoming_games = Game.query.filter(
        Game.date >= datetime.now(),
        Game.status == 'upcoming'
    ).order_by(Game.date).limit(5).all()

    # Get latest game
    latest_game = Game.query.filter(
        Game.status == 'completed'
    ).order_by(desc(Game.date)).first()

    # Get latest event (that has started)
    latest_event = Event.query.filter(
        Event.start_date <= datetime.now().date()
    ).order_by(desc(Event.start_date)).first()

    # Get top 5 scorers (all time)
    top_scorers = TeamStatistics.get_top_scorers(limit=5)

    return render_template(
        'public/index.html',
        title='Home',
        upcoming_events=upcoming_events,
        upcoming_games=upcoming_games,
        latest_game=latest_game,
        latest_event=latest_event,
        top_scorers=top_scorers
    )


@public.route('/league')
def league():
    # Get all seasons for the dropdown
    seasons = db.session.query(Event.season).filter(Event.event_type == 'league').distinct().order_by(
        desc(Event.season)).all()
    seasons = [season[0] for season in seasons]

    # Get selected season (default to most recent)
    selected_season = request.args.get('season', seasons[0] if seasons else None)

    # Get league events for the selected season
    events = Event.query.filter(
        Event.event_type == 'league',
        Event.season == selected_season
    ).order_by(Event.start_date).all()

    # Get games for the selected season's events
    event_ids = [event.id for event in events]
    games = Game.query.filter(Game.event_id.in_(event_ids)).order_by(Game.date).all()

    # Get top scorers for the selected season
    top_scorers = TeamStatistics.get_top_scorers(limit=5, season=selected_season)

    # Get team statistics for the selected season
    team_stats = TeamStatistics.get_season_stats(season=selected_season)

    return render_template(
        'public/league.html',
        title='League',
        seasons=seasons,
        selected_season=selected_season,
        events=events,
        games=games,
        top_scorers=top_scorers,
        team_stats=team_stats
    )


@public.route('/tournaments')
def tournaments():
    # Get all tournaments
    tournaments = Event.query.filter(Event.event_type == 'tournament').order_by(desc(Event.start_date)).all()

    # Get selected tournament (default to most recent)
    selected_tournament_id = request.args.get('tournament', str(tournaments[0].id) if tournaments else None)

    if selected_tournament_id:
        selected_tournament = Event.query.get(selected_tournament_id)

        # Get games for the selected tournament
        games = Game.query.filter(Game.event_id == selected_tournament_id).order_by(Game.date).all()

        # Get top scorers for the selected tournament
        from app import db
        top_scorers = db.session.query(
            Player,
            func.sum(PlayerStatistics.goals).label('total_goals')
        ).join(
            PlayerStatistics, Player.id == PlayerStatistics.player_id
        ).join(
            Game, PlayerStatistics.game_id == Game.id
        ).filter(
            Game.event_id == selected_tournament_id
        ).group_by(
            Player.id
        ).order_by(
            desc('total_goals')
        ).limit(5).all()
    else:
        selected_tournament = None
        games = []
        top_scorers = []

    return render_template(
        'public/tournaments.html',
        title='Tournaments',
        tournaments=tournaments,
        selected_tournament=selected_tournament,
        games=games,
        top_scorers=top_scorers
    )


@public.route('/statistics')
def statistics():
    # Get all players with their statistics
    players = Player.query.all()

    # Get all seasons for filters
    from app import db
    seasons = db.session.query(Event.season).distinct().order_by(desc(Event.season)).all()
    seasons = [season[0] for season in seasons]

    # Get selected season (default to all-time)
    selected_season = request.args.get('season', 'all')

    # Get team statistics for the selected season
    if selected_season == 'all':
        team_stats = TeamStatistics.get_season_stats()
    else:
        team_stats = TeamStatistics.get_season_stats(season=selected_season)

    # Filter player statistics by season if needed
    if selected_season != 'all':
        for player in players:
            filtered_stats = []
            for stat in player.statistics:
                if stat.game.event.season == selected_season:
                    filtered_stats.append(stat)
            player.statistics = filtered_stats

    return render_template(
        'public/statistics.html',
        title='Statistics',
        players=players,
        seasons=seasons,
        selected_season=selected_season,
        team_stats=team_stats
    )


@public.route('/trophies')
def trophies():
    trophies = Trophy.query.order_by(desc(Trophy.year)).all()

    # Group trophies by year
    trophy_years = {}
    for trophy in trophies:
        if trophy.year not in trophy_years:
            trophy_years[trophy.year] = []
        trophy_years[trophy.year].append(trophy)

    return render_template(
        'public/trophies.html',
        title='Trophy Cabinet',
        trophy_years=trophy_years
    )


@public.route('/players')
def players():
    players = Player.query.order_by(Player.last_name).all()

    # Get position filter
    position = request.args.get('position', 'all')

    if position != 'all':
        players = [p for p in players if p.position == position]

    # Get unique positions for filter
    from app import db
    positions = db.session.query(Player.position).distinct().order_by(Player.position).all()
    positions = [pos[0] for pos in positions]

    return render_template(
        'public/players.html',
        title='Players',
        players=players,
        positions=positions,
        selected_position=position
    )


@public.route('/players/<int:player_id>')
def player_detail(player_id):
    player = Player.query.get_or_404(player_id)

    # Get all player's games where they played
    player_games = db.session.query(Game).join(
        PlayerStatistics, PlayerStatistics.game_id == Game.id
    ).filter(
        PlayerStatistics.player_id == player_id,
        Game.status == 'completed'
    ).order_by(desc(Game.date)).all()

    # Get player's statistics for each game
    game_stats = {}
    for game in player_games:
        stat = PlayerStatistics.query.filter_by(
            player_id=player_id,
            game_id=game.id
        ).first()
        if stat:
            game_stats[game.id] = stat

    return render_template(
        'public/player_detail.html',
        title=player.full_name,
        player=player,
        player_games=player_games,
        game_stats=game_stats
    )