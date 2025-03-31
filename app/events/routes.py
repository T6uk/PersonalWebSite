# app/events/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.events.forms import EventTypeForm, EventForm, GamePlayerStatForm
from app.models.event import Event, EventType
from app.models.game_stat import GamePlayerStat
from app.models.tournament import Tournament
from app.models.user import User
from app.extensions import db
from app.utils.decorators import admin_required
from datetime import datetime

events = Blueprint('events', __name__)


@events.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    events_list = Event.query.order_by(Event.event_date.desc()).paginate(page=page, per_page=10)
    return render_template('events/index.html', title='Events', events=events_list)


@events.route('/detail/<int:event_id>')
def detail(event_id):
    event = Event.query.get_or_404(event_id)
    game_stats = GamePlayerStat.query.filter_by(event_id=event_id).all()
    return render_template('events/detail.html', title=event.title, event=event, game_stats=game_stats)


@events.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    form = EventForm()

    if form.validate_on_submit():
        tournament_id = None if form.tournament.data == 0 else form.tournament.data

        event = Event(
            title=form.title.data,
            event_type_id=form.event_type.data,
            tournament_id=tournament_id,
            opponent=form.opponent.data,
            location=form.location.data,
            event_date=form.event_date.data,
            description=form.description.data,
            result=form.result.data,
            team_score=form.team_score.data,
            opponent_score=form.opponent_score.data
        )

        db.session.add(event)
        db.session.commit()

        flash('Event has been created!', 'success')
        return redirect(url_for('events.detail', event_id=event.id))

    return render_template('events/create.html', title='Create Event', form=form)


@events.route('/update/<int:event_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def update(event_id):
    event = Event.query.get_or_404(event_id)
    form = EventForm()

    if form.validate_on_submit():
        tournament_id = None if form.tournament.data == 0 else form.tournament.data

        event.title = form.title.data
        event.event_type_id = form.event_type.data
        event.tournament_id = tournament_id
        event.opponent = form.opponent.data
        event.location = form.location.data
        event.event_date = form.event_date.data
        event.description = form.description.data
        event.result = form.result.data
        event.team_score = form.team_score.data
        event.opponent_score = form.opponent_score.data

        db.session.commit()

        flash('Event has been updated!', 'success')
        return redirect(url_for('events.detail', event_id=event.id))
    elif request.method == 'GET':
        form.title.data = event.title
        form.event_type.data = event.event_type_id
        form.tournament.data = event.tournament_id if event.tournament_id else 0
        form.opponent.data = event.opponent
        form.location.data = event.location
        form.event_date.data = event.event_date
        form.description.data = event.description
        form.result.data = event.result
        form.team_score.data = event.team_score
        form.opponent_score.data = event.opponent_score

    return render_template('events/update.html', title='Update Event', form=form, event=event)


@events.route('/delete/<int:event_id>', methods=['POST'])
@login_required
@admin_required
def delete(event_id):
    event = Event.query.get_or_404(event_id)

    db.session.delete(event)
    db.session.commit()

    flash('Event has been deleted!', 'success')
    return redirect(url_for('events.index'))


@events.route('/types')
@login_required
@admin_required
def event_types():
    event_types = EventType.query.all()
    return render_template('events/types.html', title='Event Types', event_types=event_types)


@events.route('/types/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_event_type():
    form = EventTypeForm()

    if form.validate_on_submit():
        event_type = EventType(
            name=form.name.data,
            description=form.description.data
        )

        db.session.add(event_type)
        db.session.commit()

        flash('Event type has been created!', 'success')
        return redirect(url_for('events.event_types'))

    return render_template('events/create_type.html', title='Create Event Type', form=form)


@events.route('/types/update/<int:type_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def update_event_type(type_id):
    event_type = EventType.query.get_or_404(type_id)
    form = EventTypeForm()

    if form.validate_on_submit():
        event_type.name = form.name.data
        event_type.description = form.description.data

        db.session.commit()

        flash('Event type has been updated!', 'success')
        return redirect(url_for('events.event_types'))
    elif request.method == 'GET':
        form.name.data = event_type.name
        form.description.data = event_type.description

    return render_template('events/update_type.html', title='Update Event Type', form=form, event_type=event_type)


@events.route('/types/delete/<int:type_id>', methods=['POST'])
@login_required
@admin_required
def delete_event_type(type_id):
    event_type = EventType.query.get_or_404(type_id)

    # Check if there are events using this type
    events_count = Event.query.filter_by(event_type_id=type_id).count()
    if events_count > 0:
        flash(f'Cannot delete this event type because it is used by {events_count} events.', 'danger')
        return redirect(url_for('events.event_types'))

    db.session.delete(event_type)
    db.session.commit()

    flash('Event type has been deleted!', 'success')
    return redirect(url_for('events.event_types'))


@events.route('/<int:event_id>/game_stats', methods=['GET'])
@login_required
def game_stats(event_id):
    event = Event.query.get_or_404(event_id)
    game_stats = GamePlayerStat.query.filter_by(event_id=event_id).all()

    return render_template('events/game_stats.html',
                           title='Game Statistics',
                           event=event,
                           game_stats=game_stats)


@events.route('/<int:event_id>/game_stats/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_game_stat(event_id):
    event = Event.query.get_or_404(event_id)
    form = GamePlayerStatForm()

    if form.validate_on_submit():
        # Check if player already has stats for this event
        existing = GamePlayerStat.query.filter_by(
            event_id=event_id,
            player_id=form.player.data
        ).first()

        if existing:
            flash('This player already has statistics for this event. Please update instead.', 'danger')
            return redirect(url_for('events.game_stats', event_id=event_id))

        game_stat = GamePlayerStat(
            event_id=event_id,
            player_id=form.player.data,
            minutes_played=form.minutes_played.data,
            goals=form.goals.data,
            assists=form.assists.data,
            yellow_cards=form.yellow_cards.data,
            red_cards=form.red_cards.data,
            shots=form.shots.data,
            shots_on_target=form.shots_on_target.data,
            passes=form.passes.data,
            pass_accuracy=form.pass_accuracy.data,
            tackles=form.tackles.data,
            fouls_committed=form.fouls_committed.data,
            fouls_suffered=form.fouls_suffered.data
        )

        db.session.add(game_stat)
        db.session.commit()

        flash('Player game statistics have been added!', 'success')
        return redirect(url_for('events.game_stats', event_id=event_id))

    return render_template('events/add_game_stat.html',
                           title='Add Game Statistics',
                           form=form,
                           event=event)


@events.route('/<int:event_id>/game_stats/<int:stat_id>/update', methods=['GET', 'POST'])
@login_required
@admin_required
def update_game_stat(event_id, stat_id):
    event = Event.query.get_or_404(event_id)
    game_stat = GamePlayerStat.query.get_or_404(stat_id)

    # Ensure the stat belongs to the correct event
    if game_stat.event_id != event_id:
        flash('Invalid statistics record.', 'danger')
        return redirect(url_for('events.game_stats', event_id=event_id))

    form = GamePlayerStatForm()

    if form.validate_on_submit():
        game_stat.player_id = form.player.data
        game_stat.minutes_played = form.minutes_played.data
        game_stat.goals = form.goals.data
        game_stat.assists = form.assists.data
        game_stat.yellow_cards = form.yellow_cards.data
        game_stat.red_cards = form.red_cards.data
        game_stat.shots = form.shots.data
        game_stat.shots_on_target = form.shots_on_target.data
        game_stat.passes = form.passes.data
        game_stat.pass_accuracy = form.pass_accuracy.data
        game_stat.tackles = form.tackles.data
        game_stat.fouls_committed = form.fouls_committed.data
        game_stat.fouls_suffered = form.fouls_suffered.data

        db.session.commit()

        flash('Player game statistics have been updated!', 'success')
        return redirect(url_for('events.game_stats', event_id=event_id))
    elif request.method == 'GET':
        form.player.data = game_stat.player_id
        form.minutes_played.data = game_stat.minutes_played
        form.goals.data = game_stat.goals
        form.assists.data = game_stat.assists
        form.yellow_cards.data = game_stat.yellow_cards
        form.red_cards.data = game_stat.red_cards
        form.shots.data = game_stat.shots
        form.shots_on_target.data = game_stat.shots_on_target
        form.passes.data = game_stat.passes
        form.pass_accuracy.data = game_stat.pass_accuracy
        form.tackles.data = game_stat.tackles
        form.fouls_committed.data = game_stat.fouls_committed
        form.fouls_suffered.data = game_stat.fouls_suffered

    return render_template('events/update_game_stat.html',
                           title='Update Game Statistics',
                           form=form,
                           event=event,
                           game_stat=game_stat)


@events.route('/<int:event_id>/game_stats/<int:stat_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_game_stat(event_id, stat_id):
    event = Event.query.get_or_404(event_id)
    game_stat = GamePlayerStat.query.get_or_404(stat_id)

    # Ensure the stat belongs to the correct event
    if game_stat.event_id != event_id:
        flash('Invalid statistics record.', 'danger')
        return redirect(url_for('events.game_stats', event_id=event_id))

    db.session.delete(game_stat)
    db.session.commit()

    flash('Player game statistics have been deleted!', 'success')
    return redirect(url_for('events.game_stats', event_id=event_id))