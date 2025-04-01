# app/views/admin.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, TextAreaField, DateField, \
    FloatField
from wtforms.validators import DataRequired, Email, Length, ValidationError, Optional
from ..models.User import User
from ..models.Event import Event
from ..extensions import db
from ..forms.event_forms import EventForm
from datetime import datetime
from functools import wraps

admin = Blueprint('admin', __name__, url_prefix='/admin')


# Decorator to check if user is admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('You need to be an admin to access this page.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)

    return decorated_function


class CreatePlayerForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    position = SelectField('Position', choices=[
        ('', 'Select Position'),
        ('Goalkeeper', 'Goalkeeper'),
        ('Defender', 'Defender'),
        ('Midfielder', 'Midfielder'),
        ('Forward', 'Forward')
    ])
    jersey_number = IntegerField('Jersey Number', validators=[Optional()])
    date_of_birth = DateField('Date of Birth', format='%Y-%m-%d', validators=[Optional()])
    height = FloatField('Height (cm)', validators=[Optional()])
    weight = FloatField('Weight (kg)', validators=[Optional()])
    bio = TextAreaField('Bio', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Create Player')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already in use. Please choose a different one.')


@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    player_count = User.query.filter_by(role='player').count()
    event_count = Event.query.count()
    upcoming_events_count = Event.query.filter(Event.start_datetime > datetime.utcnow()).count()
    return render_template('admin/dashboard.html', title='Admin Dashboard',
                           player_count=player_count, event_count=event_count,
                           upcoming_events_count=upcoming_events_count)


@admin.route('/create-player', methods=['GET', 'POST'])
@login_required
@admin_required
def create_player():
    form = CreatePlayerForm()
    if form.validate_on_submit():
        player = User(
            username=form.username.data,
            email=form.email.data,
            role='player',
            position=form.position.data,
            jersey_number=form.jersey_number.data,
            date_of_birth=form.date_of_birth.data,
            height=form.height.data,
            weight=form.weight.data,
            bio=form.bio.data
        )
        player.set_password(form.password.data)
        db.session.add(player)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('admin.manage_players'))
    return render_template('admin/create_player.html', title='Create Player', form=form)


@admin.route('/manage-players')
@login_required
@admin_required
def manage_players():
    players = User.query.filter_by(role='player').all()
    return render_template('admin/manage_players.html', title='Manage Players', players=players)


@admin.route('/delete-player/<int:player_id>', methods=['POST'])
@login_required
@admin_required
def delete_player(player_id):
    player = User.query.get_or_404(player_id)
    if player.role != 'player':
        flash('Can only delete player accounts.', 'danger')
        return redirect(url_for('admin.manage_players'))

    db.session.delete(player)
    db.session.commit()
    flash(f'Player {player.username} has been deleted.', 'success')
    return redirect(url_for('admin.manage_players'))


@admin.route('/events')
@login_required
@admin_required
def manage_events():
    # Get all events with statistics status
    events = Event.query.order_by(Event.start_datetime).all()

    # Get current date for comparison
    current_date = datetime.utcnow()

    return render_template('admin/manage_events.html',
                           title='Manage Events',
                           events=events,
                           current_date=current_date)


@admin.route('/events/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_event():
    form = EventForm()

    # Set season choices dynamically
    current_year = datetime.utcnow().year
    next_year = current_year + 1
    # Determine current season based on month
    current_month = datetime.utcnow().month
    if current_month >= 8:  # If after August, use current season format
        default_season = f"{current_year}-{next_year}"
    else:  # If before August, use previous season format
        default_season = f"{current_year - 1}-{current_year}"

    form.season.choices = [
        ('', 'Select Season'),
        (f"{current_year - 1}-{current_year}", f"{current_year - 1}-{current_year}"),
        (f"{current_year}-{next_year}", f"{current_year}-{next_year}")
    ]

    if request.method == 'GET':
        form.season.data = default_season

    if form.validate_on_submit():
        # Use form season or default if not provided
        season = form.season.data if form.season.data else default_season

        event = Event(
            title=form.title.data,
            description=form.description.data,
            location=form.location.data,
            event_type=form.event_type.data,
            start_datetime=form.start_datetime.data,
            end_datetime=form.end_datetime.data,
            created_by_id=current_user.id,
            season=season
        )
        db.session.add(event)
        db.session.commit()
        flash(f'Event "{form.title.data}" has been created successfully!', 'success')

        # If event is a match or tournament, redirect to add statistics
        if event.event_type in ['league_game', 'friendly_match', 'tournament']:
            flash('You can now add statistics for this event.', 'info')
            return redirect(url_for('admin_stats.event_statistics', event_id=event.id))

        return redirect(url_for('admin.manage_events'))

    return render_template('admin/create_event.html', title='Create Event', form=form)


@admin.route('/events/edit/<int:event_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    form = EventForm()

    if form.validate_on_submit():
        event.title = form.title.data
        event.description = form.description.data
        event.location = form.location.data
        event.event_type = form.event_type.data
        event.start_datetime = form.start_datetime.data
        event.end_datetime = form.end_datetime.data

        db.session.commit()
        flash(f'Event "{event.title}" has been updated successfully!', 'success')
        return redirect(url_for('admin.manage_events'))

    elif request.method == 'GET':
        form.title.data = event.title
        form.description.data = event.description
        form.location.data = event.location
        form.event_type.data = event.event_type
        form.start_datetime.data = event.start_datetime
        form.end_datetime.data = event.end_datetime

    return render_template('admin/edit_event.html', title='Edit Event', form=form, event=event)


@admin.route('/events/delete/<int:event_id>', methods=['POST'])
@login_required
@admin_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash(f'Event "{event.title}" has been deleted.', 'success')
    return redirect(url_for('admin.manage_events'))