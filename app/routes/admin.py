from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.player import Player
from app.models.event import Event
from app.models.game import Game
from app.models.statistics import PlayerStatistics
from app.models.trophy import Trophy
from app.forms.player import PlayerForm
from app.forms.event import EventForm
from app.forms.game import GameForm, GameResultForm, GameStatsForm
from app.forms.trophy import TrophyForm
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
    event_count = Event.query.count()
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
        event_count=event_count,
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
            is_active=form.is_active.data,
            # Add career statistics
            career_appearances=form.career_appearances.data,
            career_goals=form.career_goals.data,
            career_assists=form.career_assists.data,
            career_yellow_cards=form.career_yellow_cards.data,
            career_red_cards=form.career_red_cards.data,
            career_minutes_played=form.career_minutes_played.data
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
        # Update career statistics
        player.career_appearances = form.career_appearances.data
        player.career_goals = form.career_goals.data
        player.career_assists = form.career_assists.data
        player.career_yellow_cards = form.career_yellow_cards.data
        player.career_red_cards = form.career_red_cards.data
        player.career_minutes_played = form.career_minutes_played.data

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


# Events
@admin.route('/events')
@login_required
def events():
    events = Event.query.order_by(Event.start_date.desc()).all()
    return render_template('admin/events.html', title='Manage Events', events=events)


@admin.route('/events/add', methods=['GET', 'POST'])
@login_required
def add_event():
    form = EventForm()

    if form.validate_on_submit():
        event = Event(
            name=form.name.data,
            event_type=form.event_type.data,
            season=form.season.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            location=form.location.data,
            description=form.description.data
        )

        if form.image.data:
            event.image_url = save_file(form.image.data, 'events')

        db.session.add(event)
        db.session.commit()

        flash(f'Event {event.name} has been added!', 'success')
        return redirect(url_for('admin.events'))

    return render_template('admin/event_form.html', title='Add Event', form=form)


@admin.route('/events/edit/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    form = EventForm(obj=event)

    if form.validate_on_submit():
        event.name = form.name.data
        event.event_type = form.event_type.data
        event.season = form.season.data
        event.start_date = form.start_date.data
        event.end_date = form.end_date.data
        event.location = form.location.data
        event.description = form.description.data

        if form.image.data:
            event.image_url = save_file(form.image.data, 'events')

        db.session.commit()

        flash(f'Event {event.name} has been updated!', 'success')
        return redirect(url_for('admin.events'))

    return render_template('admin/event_form.html', title='Edit Event', form=form, event=event)


@admin.route('/events/delete/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    name = event.name

    db.session.delete(event)
    db.session.commit()

    flash(f'Event {name} has been deleted!', 'success')
    return redirect(url_for('admin.events'))


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
    # Populate event choices
    form.event_id.choices = [(e.id, f"{e.name} ({e.season})") for e in
                             Event.query.order_by(Event.start_date.desc()).all()]

    if form.validate_on_submit():
        game = Game(
            event_id=form.event_id.data,
            opponent=form.opponent.data,
            date=form.date.data,
            location=form.location.data,
            is_home_game=form.is_home_game.data,
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
    # Populate event choices
    form.event_id.choices = [(e.id, f"{e.name} ({e.season})") for e in
                             Event.query.order_by(Event.start_date.desc()).all()]

    if form.validate_on_submit():
        game.event_id = form.event_id.data
        game.opponent = form.opponent.data
        game.date = form.date.data
        game.location = form.location.data
        game.is_home_game = form.is_home_game.data
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
