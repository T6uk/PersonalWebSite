from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('player.dashboard'))
    return redirect(url_for('auth.login'))

@main.route('/home')
@login_required
def home():
    return render_template('home.html', title='Home')