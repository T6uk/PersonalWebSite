from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps

player = Blueprint('player', __name__, url_prefix='/player')

# Decorator to check if user is a player
def player_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_player():
            flash('You need to be a player to access this page.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

@player.route('/dashboard')
@login_required
@player_required
def dashboard():
    return render_template('player/dashboard.html', title='Player Dashboard')