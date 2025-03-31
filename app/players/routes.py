from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.players.forms import UpdateProfileForm
from app.models.user import User
from app.models.statistic import PlayerStatistic
from app.extensions import db
from app.utils.files import save_picture
import os

players = Blueprint('players', __name__)


@players.route('/dashboard')
@login_required
def dashboard():
    # Get player's statistics
    stats = PlayerStatistic.query.filter_by(player_id=current_user.id).order_by(PlayerStatistic.season.desc()).all()
    return render_template('players/dashboard.html', title='Player Dashboard', stats=stats)


@players.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        if form.profile_picture.data:
            if current_user.profile_picture != 'default.jpg':
                # Delete old profile picture
                old_picture_path = os.path.join(current_app.root_path, 'static/uploads', current_user.profile_picture)
                if os.path.exists(old_picture_path):
                    os.remove(old_picture_path)

            picture_file = save_picture(form.profile_picture.data)
            current_user.profile_picture = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data

        if form.new_password.data:
            current_user.set_password(form.new_password.data)

        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('players.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name

    return render_template('players/profile.html', title='Profile', form=form)