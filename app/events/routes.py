from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.events.forms import EventTypeForm, EventForm
from app.models.event import Event, EventType
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
    return render_template('events/detail.html', title=event.title, event=event)


# app/events/routes.py (update the create function)

@events.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    # Check if we're adding a sub-event to a tournament
    parent_id = request.args.get('parent', type=int)
    parent_event = None
    if parent_id:
        parent_event = Event.query.get_or_404(parent_id)
        if not parent_event.is_tournament:
            flash('You can only add games to tournament events.', 'danger')
            return redirect(url_for('events.detail', event_id=parent_id))

    form = EventForm()

    if form.validate_on_submit():
        # If we're creating a game for a tournament, use the parent_id from args
        if parent_id:
            actual_parent_id = parent_id
        else:
            actual_parent_id = None if form.parent_event.data == 0 else form.parent_event.data

        event = Event(
            title=form.title.data,
            event_type_id=form.event_type.data,
            parent_id=actual_parent_id,
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
        if parent_id:
            return redirect(url_for('events.detail', event_id=parent_id))
        else:
            return redirect(url_for('events.detail', event_id=event.id))

    # If we're creating a sub-event, preset some values
    if parent_event:
        form.parent_event.data = parent_event.id
        form.location.data = parent_event.location

        # Find a non-tournament event type for the sub-event
        match_type = EventType.query.filter_by(name='Match').first() or \
                     EventType.query.filter_by(name='Game').first() or \
                     EventType.query.filter(EventType.name != 'Tournament').first()
        if match_type:
            form.event_type.data = match_type.id

    return render_template('events/create.html',
                           title='Create Event',
                           form=form,
                           parent_event=parent_event)


@events.route('/update/<int:event_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def update(event_id):
    event = Event.query.get_or_404(event_id)
    form = EventForm()

    if form.validate_on_submit():
        parent_id = None if form.parent_event.data == 0 else form.parent_event.data

        # Don't allow circular references
        if parent_id == event.id:
            flash('An event cannot be its own parent!', 'danger')
            return redirect(url_for('events.update', event_id=event.id))

        event.title = form.title.data
        event.event_type_id = form.event_type.data
        event.parent_id = parent_id
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
        form.parent_event.data = event.parent_id if event.parent_id else 0
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