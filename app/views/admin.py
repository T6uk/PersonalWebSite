from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, TextAreaField, DateField, \
    FloatField
from wtforms.validators import DataRequired, Email, Length, ValidationError, Optional
from ..models.user import User
from ..extensions import db
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
    return render_template('admin/dashboard.html', title='Admin Dashboard', player_count=player_count)


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