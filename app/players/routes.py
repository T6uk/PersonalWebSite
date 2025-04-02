from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.players import bp
from app.players.forms import PlayerProfileForm
from app.models import User, PlayerProfile
from functools import wraps


def coach_or_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or (not current_user.is_coach() and not current_user.is_admin()):
            flash('You do not have permission to access this page', 'danger')
            return redirect(url_for('core.home'))
        return f(*args, **kwargs)

    return decorated_function


@bp.route('/list')
@login_required
@coach_or_admin_required
def list_players():
    players = User.query.filter_by(role='player').all()
    return render_template('players/list_players.html', title='Players List', players=players)


@bp.route('/profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def player_profile(user_id):
    # Players can only view their own profile
    if not current_user.is_admin() and not current_user.is_coach() and current_user.id != user_id:
        flash('You do not have permission to view this profile', 'danger')
        return redirect(url_for('core.home'))

    user = User.query.get_or_404(user_id)
    profile = PlayerProfile.query.filter_by(user_id=user.id).first()

    if not profile and (current_user.is_admin() or current_user.is_coach() or current_user.id == user_id):
        # Create an empty profile if none exists
        profile = PlayerProfile(user_id=user.id)
        db.session.add(profile)
        db.session.commit()

    form = PlayerProfileForm(obj=profile)

    # Only coaches and admins can edit profiles
    can_edit = current_user.is_admin() or current_user.is_coach()

    if form.validate_on_submit() and can_edit:
        form.populate_obj(profile)
        db.session.commit()
        flash('Player profile updated successfully', 'success')
        return redirect(url_for('players.player_profile', user_id=user.id))

    return render_template('players/profile.html',
                           title=f'{user.username}\'s Profile',
                           user=user,
                           profile=profile,
                           form=form,
                           can_edit=can_edit)