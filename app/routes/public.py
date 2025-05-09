from flask import Blueprint, render_template, request, current_app
from app.models.player import Player
from app.models.game import Game
from app.models.statistics import PlayerStatistics, TeamStatistics
from app.models.trophy import Trophy
from app.models.season import Season
from app.models.competition import Competition
from app.models.league import League
from app.models.tournament import Tournament
from app.models.friendly import Friendly
from sqlalchemy import desc, func
from datetime import datetime
from app import db

public = Blueprint('public', __name__)


@public.route('/')
def index():
    # Get current season
    current_season = Season.query.filter_by(is_current=True).first()

    # Get upcoming events
    upcoming_competitions = Competition.query.filter(
        Competition.start_date >= datetime.now().date()
    ).order_by(Competition.start_date).limit(3).all()

    # Get upcoming games
    upcoming_games = Game.query.filter(
        Game.date >= datetime.now(),
        Game.status == 'upcoming'
    ).order_by(Game.date).limit(5).all()

    # Get latest game
    latest_game = Game.query.filter(
        Game.status == 'completed'
    ).order_by(desc(Game.date)).first()

    # Get latest competition (that has started)
    latest_competition = Competition.query.filter(
        Competition.start_date <= datetime.now().date()
    ).order_by(desc(Competition.start_date)).first()

    # Get top 5 scorers (all time)
    top_scorers = TeamStatistics.get_top_scorers(limit=5)

    return render_template(
        'public/index.html',
        title='Home',
        upcoming_events=upcoming_competitions,
        upcoming_games=upcoming_games,
        latest_game=latest_game,
        latest_event=latest_competition,
        top_scorers=top_scorers,
        current_season=current_season
    )


@public.route('/league')
def league():
    # Get all seasons for the dropdown
    seasons = Season.query.order_by(desc(Season.start_date)).all()

    # Early return if no seasons exist
    if not seasons:
        return render_template(
            'public/league.html',
            title='League',
            seasons=[],
            selected_season=None,
            leagues=[],
            games=[],
            top_scorers=[],
            team_stats=None
        )

    # Get selected season (default to current season, if any, or most recent)
    current_season = Season.query.filter_by(is_current=True).first()

    # Handle the case where no season ID is in the URL and safely get a default
    if 'season' in request.args:
        selected_season_id = request.args.get('season')
    else:
        # Default to current or first season, with safe handling
        if current_season:
            selected_season_id = str(current_season.id)
        elif seasons:
            selected_season_id = str(seasons[0].id)
        else:
            selected_season_id = None

    if selected_season_id:
        selected_season = Season.query.get(selected_season_id)

        # Get leagues for the selected season
        leagues = League.query.filter_by(season_id=selected_season_id).order_by(League.start_date).all()

        # Get games for the selected season's leagues (safely handle empty list)
        league_ids = [league.id for league in leagues]
        games = Game.query.filter(Game.competition_id.in_(league_ids)).order_by(Game.date).all() if league_ids else []

        # Get top scorers and stats, safely handling the selected_season.name
        if selected_season:
            top_scorers = TeamStatistics.get_top_scorers(limit=5, season=selected_season.name)
            team_stats = TeamStatistics.get_season_stats(season=selected_season.name)
        else:
            top_scorers = []
            team_stats = None

        return render_template(
            'public/league.html',
            title='League',
            seasons=seasons,
            selected_season=selected_season,
            leagues=leagues,
            games=games,
            top_scorers=top_scorers,
            team_stats=team_stats
        )
    else:
        return render_template(
            'public/league.html',
            title='League',
            seasons=seasons,
            selected_season=None,
            leagues=[],
            games=[],
            top_scorers=[],
            team_stats=None
        )


@public.route('/tournaments')
def tournaments():
    # Get all seasons for the dropdown
    seasons = Season.query.order_by(desc(Season.start_date)).all()

    # Get selected season (default to current season)
    current_season = Season.query.filter_by(is_current=True).first()
    selected_season_id = request.args.get('season', str(current_season.id if current_season else (
        seasons[0].id if seasons else None)))

    # Get selected tournament
    selected_tournament_id = request.args.get('tournament')

    if selected_season_id:
        # Get tournaments for the selected season
        tournaments = Tournament.query.filter_by(season_id=selected_season_id).order_by(Tournament.start_date).all()

        # If no tournament is selected but there are tournaments, select the first one
        if not selected_tournament_id and tournaments:
            selected_tournament_id = str(tournaments[0].id)

        if selected_tournament_id:
            selected_tournament = Tournament.query.get(selected_tournament_id)

            # Get games for the selected tournament
            games = Game.query.filter_by(competition_id=selected_tournament_id).order_by(Game.date).all()

            # Get top scorers for the selected tournament
            top_scorers = db.session.query(
                Player,
                func.sum(PlayerStatistics.goals).label('total_goals')
            ).join(
                PlayerStatistics, Player.id == PlayerStatistics.player_id
            ).join(
                Game, PlayerStatistics.game_id == Game.id
            ).filter(
                Game.competition_id == selected_tournament_id
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
            seasons=seasons,
            selected_season=Season.query.get(selected_season_id),
            tournaments=tournaments,
            selected_tournament=selected_tournament,
            games=games,
            top_scorers=top_scorers
        )
    else:
        return render_template(
            'public/tournaments.html',
            title='Tournaments',
            seasons=seasons,
            selected_season=None
        )


@public.route('/friendlies')
def friendlies():
    # Get all seasons for the dropdown
    seasons = Season.query.order_by(desc(Season.start_date)).all()

    # Get selected season (default to current season)
    current_season = Season.query.filter_by(is_current=True).first()
    selected_season_id = request.args.get('season', str(current_season.id if current_season else (
        seasons[0].id if seasons else None)))

    if selected_season_id:
        # Get friendlies for the selected season
        friendlies = Friendly.query.filter_by(season_id=selected_season_id).order_by(Friendly.start_date.desc()).all()

        # Get games for the selected season's friendlies
        friendly_ids = [friendly.id for friendly in friendlies]
        games = Game.query.filter(Game.competition_id.in_(friendly_ids)).order_by(Game.date).all()

        return render_template(
            'public/friendlies.html',
            title='Friendlies',
            seasons=seasons,
            selected_season=Season.query.get(selected_season_id),
            friendlies=friendlies,
            games=games
        )
    else:
        return render_template(
            'public/friendlies.html',
            title='Friendlies',
            seasons=seasons,
            selected_season=None
        )


@public.route('/statistics')
def statistics():
    # Get all players with their statistics
    players = Player.query.all()

    # Get all seasons for filters
    seasons = Season.query.order_by(desc(Season.start_date)).all()
    season_names = [season.name for season in seasons]

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
                if stat.game.competition.season.name == selected_season:
                    filtered_stats.append(stat)
            player.statistics = filtered_stats

    return render_template(
        'public/statistics.html',
        title='Statistics',
        players=players,
        seasons=season_names,
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