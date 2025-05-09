from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.player import Player
from app.models.game import Game
from app.models.statistics import PlayerStatistics
from app.models.trophy import Trophy
from app.models.season import Season
from app.models.competition import Competition
from app.models.league import League
from app.models.tournament import Tournament
from app.models.friendly import Friendly
from app.forms.player import PlayerForm
from app.forms.game import GameForm, GameResultForm, GameStatsForm
from app.forms.trophy import TrophyForm
from app.forms.season import SeasonForm
from app.forms.competition import LeagueForm, TournamentForm, FriendlyForm
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import uuid

admin = Blueprint('admin', __name__, url_prefix='/admin')


# Helper function for file uploads
def save_file(file, folder='uploads'):
    if not file:
        return None

    filename = secure_filename(file.filename)
    # Add unique identifier to prevent filename collisions
    unique_filename = f"{uuid.uuid4().hex}_{filename}"

    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)

    # Ensure the upload folder exists
    os.makedirs(upload_folder, exist_ok=True)

    file_path = os.path.join(upload_folder, unique_filename)
    file.save(file_path)

    # Return the relative path for storage in the database
    return f'/static/uploads/{folder}/{unique_filename}'


# Dashboard
@admin.route('/')
@login_required
def dashboard():
    # Get counts for statistics
    player_count = Player.query.count()
    competition_count = Competition.query.count()
    upcoming_games_count = Game.query.filter(Game.date > datetime.now(), Game.status == 'upcoming').count()
    trophy_count = Trophy.query.count()

    # Get recent games
    recent_games = Game.query.filter(Game.status == 'completed').order_by(Game.date.desc()).limit(5).all()

    # Get upcoming games
    upcoming_games = Game.query.filter(Game.date > datetime.now(), Game.status == 'upcoming').order_by(Game.date).limit(
        5).all()

    return render_template(
        'admin/dashboard.html',
        title='Admin Dashboard',
        player_count=player_count,
        competition_count=competition_count,
        upcoming_games_count=upcoming_games_count,
        trophy_count=trophy_count,
        recent_games=recent_games,
        upcoming_games=upcoming_games
    )


# Players
@admin.route('/players')
@login_required
def players():
    players = Player.query.order_by(Player.last_name).all()
    return render_template('admin/players.html', title='Manage Players', players=players)


@admin.route('/players/add', methods=['GET', 'POST'])
@login_required
def add_player():
    form = PlayerForm()

    if form.validate_on_submit():
        player = Player(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            position=form.position.data,
            jersey_number=form.jersey_number.data,
            date_of_birth=form.date_of_birth.data,
            height=form.height.data,
            weight=form.weight.data,
            nationality=form.nationality.data,
            bio=form.bio.data,
            is_active=form.is_active.data
        )

        if form.image.data:
            player.image_url = save_file(form.image.data, 'players')

        db.session.add(player)
        db.session.commit()

        flash(f'Player {player.full_name} has been added!', 'success')
        return redirect(url_for('admin.players'))

    return render_template('admin/player_form.html', title='Add Player', form=form)


@admin.route('/players/edit/<int:player_id>', methods=['GET', 'POST'])
@login_required
def edit_player(player_id):
    player = Player.query.get_or_404(player_id)
    form = PlayerForm(obj=player)

    if form.validate_on_submit():
        player.first_name = form.first_name.data
        player.last_name = form.last_name.data
        player.position = form.position.data
        player.jersey_number = form.jersey_number.data
        player.date_of_birth = form.date_of_birth.data
        player.height = form.height.data
        player.weight = form.weight.data
        player.nationality = form.nationality.data
        player.bio = form.bio.data
        player.is_active = form.is_active.data

        if form.image.data:
            player.image_url = save_file(form.image.data, 'players')

        db.session.commit()

        flash(f'Player {player.full_name} has been updated!', 'success')
        return redirect(url_for('admin.players'))

    return render_template('admin/player_form.html', title='Edit Player', form=form, player=player)


@admin.route('/players/delete/<int:player_id>', methods=['POST'])
@login_required
def delete_player(player_id):
    player = Player.query.get_or_404(player_id)
    name = player.full_name

    db.session.delete(player)
    db.session.commit()

    flash(f'Player {name} has been deleted!', 'success')
    return redirect(url_for('admin.players'))


# Season Management
@admin.route('/seasons')
@login_required
def seasons():
    seasons = Season.query.order_by(Season.start_date.desc()).all()
    return render_template('admin/seasons.html', title='Manage Seasons', seasons=seasons)


@admin.route('/seasons/add', methods=['GET', 'POST'])
@login_required
def add_season():
    form = SeasonForm()

    if form.validate_on_submit():
        # If this is marked as current season, set all others to not current
        if form.is_current.data:
            current_seasons = Season.query.filter_by(is_current=True).all()
            for season in current_seasons:
                season.is_current = False

        season = Season(
            name=form.name.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            is_current=form.is_current.data
        )

        db.session.add(season)
        db.session.commit()

        flash(f'Season {season.name} has been added!', 'success')
        return redirect(url_for('admin.seasons'))

    return render_template('admin/season_form.html', title='Add Season', form=form)


@admin.route('/seasons/edit/<int:season_id>', methods=['GET', 'POST'])
@login_required
def edit_season(season_id):
    season = Season.query.get_or_404(season_id)
    form = SeasonForm(obj=season)

    if form.validate_on_submit():
        # If this is marked as current season, set all others to not current
        if form.is_current.data and not season.is_current:
            current_seasons = Season.query.filter_by(is_current=True).all()
            for current_season in current_seasons:
                current_season.is_current = False

        season.name = form.name.data
        season.start_date = form.start_date.data
        season.end_date = form.end_date.data
        season.is_current = form.is_current.data

        db.session.commit()

        flash(f'Season {season.name} has been updated!', 'success')
        return redirect(url_for('admin.seasons'))

    return render_template('admin/season_form.html', title='Edit Season', form=form, season=season)


@admin.route('/seasons/delete/<int:season_id>', methods=['POST'])
@login_required
def delete_season(season_id):
    season = Season.query.get_or_404(season_id)
    name = season.name

    db.session.delete(season)
    db.session.commit()

    flash(f'Season {name} has been deleted!', 'success')
    return redirect(url_for('admin.seasons'))


# League Management
@admin.route('/leagues')
@login_required
def leagues():
    leagues = League.query.order_by(League.start_date.desc()).all()
    return render_template('admin/leagues.html', title='Manage Leagues', leagues=leagues)


@admin.route('/leagues/add', methods=['GET', 'POST'])
@login_required
def add_league():
    form = LeagueForm()
    # Populate season choices
    form.season_id.choices = [(s.id, s.name) for s in Season.query.order_by(Season.start_date.desc()).all()]

    if form.validate_on_submit():
        league = League(
            name=form.name.data,
            season_id=form.season_id.data,
            competition_type='league',  # Set explicitly
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            location=form.location.data,
            description=form.description.data,
            format=form.format.data,
            num_teams=form.num_teams.data,
            points_for_win=form.points_for_win.data,
            points_for_draw=form.points_for_draw.data
        )

        if form.image.data:
            league.image_url = save_file(form.image.data, 'leagues')

        db.session.add(league)
        db.session.commit()

        flash(f'League {league.name} has been added!', 'success')
        return redirect(url_for('admin.leagues'))

    return render_template('admin/league_form.html', title='Add League', form=form)


@admin.route('/leagues/edit/<int:league_id>', methods=['GET', 'POST'])
@login_required
def edit_league(league_id):
    league = League.query.get_or_404(league_id)
    form = LeagueForm(obj=league)
    # Populate season choices
    form.season_id.choices = [(s.id, s.name) for s in Season.query.order_by(Season.start_date.desc()).all()]

    if form.validate_on_submit():
        league.name = form.name.data
        league.season_id = form.season_id.data
        league.start_date = form.start_date.data
        league.end_date = form.end_date.data
        league.location = form.location.data
        league.description = form.description.data
        league.format = form.format.data
        league.num_teams = form.num_teams.data
        league.points_for_win = form.points_for_win.data
        league.points_for_draw = form.points_for_draw.data

        if form.image.data:
            league.image_url = save_file(form.image.data, 'leagues')

        db.session.commit()

        flash(f'League {league.name} has been updated!', 'success')
        return redirect(url_for('admin.leagues'))

    return render_template('admin/league_form.html', title='Edit League', form=form, league=league)


@admin.route('/leagues/delete/<int:league_id>', methods=['POST'])
@login_required
def delete_league(league_id):
    league = League.query.get_or_404(league_id)
    name = league.name

    db.session.delete(league)
    db.session.commit()

    flash(f'League {name} has been deleted!', 'success')
    return redirect(url_for('admin.leagues'))


# Tournament Management
@admin.route('/tournaments_admin')
@login_required
def tournaments_admin():
    tournaments = Tournament.query.order_by(Tournament.start_date.desc()).all()
    return render_template('admin/tournaments.html', title='Manage Tournaments', tournaments=tournaments)


@admin.route('/tournaments/add', methods=['GET', 'POST'])
@login_required
def add_tournament():
    form = TournamentForm()
    # Populate season choices
    form.season_id.choices = [(s.id, s.name) for s in Season.query.order_by(Season.start_date.desc()).all()]

    if form.validate_on_submit():
        tournament = Tournament(
            name=form.name.data,
            season_id=form.season_id.data,
            competition_type='tournament',  # Set explicitly
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            location=form.location.data,
            description=form.description.data,
            format=form.format.data,
            num_teams=form.num_teams.data,
            current_round=form.current_round.data
        )

        if form.image.data:
            tournament.image_url = save_file(form.image.data, 'tournaments')

        db.session.add(tournament)
        db.session.commit()

        flash(f'Tournament {tournament.name} has been added!', 'success')
        return redirect(url_for('admin.tournaments_admin'))

    return render_template('admin/tournament_form.html', title='Add Tournament', form=form)


@admin.route('/tournaments/edit/<int:tournament_id>', methods=['GET', 'POST'])
@login_required
def edit_tournament(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    form = TournamentForm(obj=tournament)
    # Populate season choices
    form.season_id.choices = [(s.id, s.name) for s in Season.query.order_by(Season.start_date.desc()).all()]

    if form.validate_on_submit():
        tournament.name = form.name.data
        tournament.season_id = form.season_id.data
        tournament.start_date = form.start_date.data
        tournament.end_date = form.end_date.data
        tournament.location = form.location.data
        tournament.description = form.description.data
        tournament.format = form.format.data
        tournament.num_teams = form.num_teams.data
        tournament.current_round = form.current_round.data

        if form.image.data:
            tournament.image_url = save_file(form.image.data, 'tournaments')

        db.session.commit()

        flash(f'Tournament {tournament.name} has been updated!', 'success')
        return redirect(url_for('admin.tournaments_admin'))

    return render_template('admin/tournament_form.html', title='Edit Tournament', form=form, tournament=tournament)


@admin.route('/tournaments/delete/<int:tournament_id>', methods=['POST'])
@login_required
def delete_tournament(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    name = tournament.name

    db.session.delete(tournament)
    db.session.commit()

    flash(f'Tournament {name} has been deleted!', 'success')
    return redirect(url_for('admin.tournaments_admin'))


# Friendly Management
@admin.route('/friendlies_admin')
@login_required
def friendlies_admin():
    friendlies = Friendly.query.order_by(Friendly.start_date.desc()).all()
    return render_template('admin/friendlies.html', title='Manage Friendlies', friendlies=friendlies)


@admin.route('/friendlies/add', methods=['GET', 'POST'])
@login_required
def add_friendly():
    form = FriendlyForm()
    # Populate season choices
    form.season_id.choices = [(s.id, s.name) for s in Season.query.order_by(Season.start_date.desc()).all()]

    if form.validate_on_submit():
        friendly = Friendly(
            name=form.name.data,
            season_id=form.season_id.data,
            competition_type='friendly',  # Set explicitly
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            location=form.location.data,
            description=form.description.data,
            purpose=form.purpose.data
        )

        if form.image.data:
            friendly.image_url = save_file(form.image.data, 'friendlies')

        db.session.add(friendly)
        db.session.commit()

        flash(f'Friendly {friendly.name} has been added!', 'success')
        return redirect(url_for('admin.friendlies_admin'))

    return render_template('admin/friendly_form.html', title='Add Friendly', form=form)


@admin.route('/friendlies/edit/<int:friendly_id>', methods=['GET', 'POST'])
@login_required
def edit_friendly(friendly_id):
    friendly = Friendly.query.get_or_404(friendly_id)
    form = FriendlyForm(obj=friendly)
    # Populate season choices
    form.season_id.choices = [(s.id, s.name) for s in Season.query.order_by(Season.start_date.desc()).all()]

    if form.validate_on_submit():
        friendly.name = form.name.data
        friendly.season_id = form.season_id.data
        friendly.start_date = form.start_date.data
        friendly.end_date = form.end_date.data
        friendly.location = form.location.data
        friendly.description = form.description.data
        friendly.purpose = form.purpose.data

        if form.image.data:
            friendly.image_url = save_file(form.image.data, 'friendlies')

        db.session.commit()

        flash(f'Friendly {friendly.name} has been updated!', 'success')
        return redirect(url_for('admin.friendlies_admin'))

    return render_template('admin/friendly_form.html', title='Edit Friendly', form=form, friendly=friendly)


@admin.route('/friendlies/delete/<int:friendly_id>', methods=['POST'])
@login_required
def delete_friendly(friendly_id):
    friendly = Friendly.query.get_or_404(friendly_id)
    name = friendly.name

    db.session.delete(friendly)
    db.session.commit()

    flash(f'Friendly {name} has been deleted!', 'success')
    return redirect(url_for('admin.friendlies_admin'))


# Games
@admin.route('/games')
@login_required
def games():
    games = Game.query.order_by(Game.date.desc()).all()
    return render_template('admin/games.html', title='Manage Games', games=games)


@admin.route('/games/add', methods=['GET', 'POST'])
@login_required
def add_game():
    form = GameForm()
    # Populate competition choices
    form.competition_id.choices = [(c.id, f"{c.name} ({c.season.name}) - {c.competition_type.capitalize()}")
                                  for c in Competition.query.join(Season).order_by(Season.start_date.desc()).all()]

    if form.validate_on_submit():
        game = Game(
            competition_id=form.competition_id.data,
            opponent=form.opponent.data,
            date=form.date.data,
            location=form.location.data,
            is_home_game=form.is_home_game.data,
            round=form.round.data,
            matchday=form.matchday.data,
            notes=form.notes.data,
            status='upcoming'
        )

        db.session.add(game)
        db.session.commit()

        flash(f'Game vs {game.opponent} has been added!', 'success')
        return redirect(url_for('admin.games'))

    return render_template('admin/game_form.html', title='Add Game', form=form)


@admin.route('/games/edit/<int:game_id>', methods=['GET', 'POST'])
@login_required
def edit_game(game_id):
    game = Game.query.get_or_404(game_id)
    form = GameForm(obj=game)
    # Populate competition choices
    form.competition_id.choices = [(c.id, f"{c.name} ({c.season.name}) - {c.competition_type.capitalize()}")
                                  for c in Competition.query.join(Season).order_by(Season.start_date.desc()).all()]

    if form.validate_on_submit():
        game.competition_id = form.competition_id.data
        game.opponent = form.opponent.data
        game.date = form.date.data
        game.location = form.location.data
        game.is_home_game = form.is_home_game.data
        game.round = form.round.data
        game.matchday = form.matchday.data
        game.notes = form.notes.data

        db.session.commit()

        flash(f'Game vs {game.opponent} has been updated!', 'success')
        return redirect(url_for('admin.games'))

    return render_template('admin/game_form.html', title='Edit Game', form=form, game=game)


@admin.route('/games/delete/<int:game_id>', methods=['POST'])
@login_required
def delete_game(game_id):
    game = Game.query.get_or_404(game_id)
    opponent = game.opponent

    db.session.delete(game)
    db.session.commit()

    flash(f'Game vs {opponent} has been deleted!', 'success')
    return redirect(url_for('admin.games'))


@admin.route('/games/result/<int:game_id>', methods=['GET', 'POST'])
@login_required
def game_result(game_id):
    game = Game.query.get_or_404(game_id)
    form = GameResultForm(obj=game)

    if form.validate_on_submit():
        game.score_team = form.score_team.data
        game.score_opponent = form.score_opponent.data
        game.status = form.status.data
        game.highlights_url = form.highlights_url.data
        game.notes = form.notes.data

        db.session.commit()

        flash(f'Result for game vs {game.opponent} has been saved!', 'success')
        return redirect(url_for('admin.games'))

    return render_template('admin/game_result_form.html', title='Enter Game Result', form=form, game=game)


@admin.route('/games/statistics/<int:game_id>', methods=['GET', 'POST'])
@login_required
def game_statistics(game_id):
    game = Game.query.get_or_404(game_id)

    # Only allow statistics for completed games
    if game.status != 'completed':
        flash('Cannot add statistics for games that are not completed.', 'warning')
        return redirect(url_for('admin.games'))

    # Get active players
    players = Player.query.filter_by(is_active=True).order_by(Player.last_name).all()
    player_choices = [(p.id, p.full_name) for p in players]

    # Check if stats already exist
    existing_stats = PlayerStatistics.query.filter_by(game_id=game_id).all()

    # Create form with existing stats or empty form
    if request.method == 'GET':
        if existing_stats:
            # Pre-populate form with existing stats
            form = GameStatsForm(player_stats=[{
                'player_id': stat.player_id,
                'goals': stat.goals,
                'assists': stat.assists,
                'minutes_played': stat.minutes_played,
                'yellow_cards': stat.yellow_cards,
                'red_cards': stat.red_cards,
                'shots': stat.shots,
                'shots_on_target': stat.shots_on_target,
                'rating': stat.rating,
                'notes': stat.notes
            } for stat in existing_stats])
        else:
            # Create empty form with one entry
            form = GameStatsForm()
    else:
        form = GameStatsForm()

    # Set player choices for all form entries
    for entry in form.player_stats:
        entry.player_id.choices = player_choices

    if form.validate_on_submit():
        # Delete existing stats
        for stat in existing_stats:
            db.session.delete(stat)

        # Add new stats
        for stat_form in form.player_stats.data:
            stat = PlayerStatistics(
                player_id=stat_form['player_id'],
                game_id=game_id,
                goals=stat_form['goals'],
                assists=stat_form['assists'],
                minutes_played=stat_form['minutes_played'],
                yellow_cards=stat_form['yellow_cards'],
                red_cards=stat_form['red_cards'],
                shots=stat_form['shots'],
                shots_on_target=stat_form['shots_on_target'],
                rating=stat_form['rating'],
                notes=stat_form['notes']
            )
            db.session.add(stat)

        db.session.commit()
        flash('Player statistics have been saved!', 'success')
        return redirect(url_for('admin.games'))

    return render_template('admin/game_stats_form.html', title='Player Statistics', form=form, game=game)


# Trophies
@admin.route('/trophies')
@login_required
def trophies():
    trophies = Trophy.query.order_by(Trophy.year.desc()).all()
    return render_template('admin/trophies.html', title='Manage Trophies', trophies=trophies)


@admin.route('/trophies/add', methods=['GET', 'POST'])
@login_required
def add_trophy():
    form = TrophyForm()

    if form.validate_on_submit():
        trophy = Trophy(
            name=form.name.data,
            competition=form.competition.data,
            year=form.year.data,
            description=form.description.data
        )

        if form.image.data:
            trophy.image_url = save_file(form.image.data, 'trophies')

        db.session.add(trophy)
        db.session.commit()

        flash(f'Trophy {trophy.name} has been added!', 'success')
        return redirect(url_for('admin.trophies'))

    return render_template('admin/trophy_form.html', title='Add Trophy', form=form)


@admin.route('/trophies/edit/<int:trophy_id>', methods=['GET', 'POST'])
@login_required
def edit_trophy(trophy_id):
    trophy = Trophy.query.get_or_404(trophy_id)
    form = TrophyForm(obj=trophy)

    if form.validate_on_submit():
        trophy.name = form.name.data
        trophy.competition = form.competition.data
        trophy.year = form.year.data
        trophy.description = form.description.data

        if form.image.data:
            trophy.image_url = save_file(form.image.data, 'trophies')

        db.session.commit()

        flash(f'Trophy {trophy.name} has been updated!', 'success')
        return redirect(url_for('admin.trophies'))

    return render_template('admin/trophy_form.html', title='Edit Trophy', form=form, trophy=trophy)


@admin.route('/trophies/delete/<int:trophy_id>', methods=['POST'])
@login_required
def delete_trophy(trophy_id):
    trophy = Trophy.query.get_or_404(trophy_id)
    name = trophy.name

    db.session.delete(trophy)
    db.session.commit()

    flash(f'Trophy {name} has been deleted!', 'success')
    return redirect(url_for('admin.trophies'))