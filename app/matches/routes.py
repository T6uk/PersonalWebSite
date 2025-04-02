from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.matches import bp
from app.matches.forms import MatchForm
from app.models import Match
from app.admin.routes import admin_required
from functools import wraps
import datetime


def coach_or_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or (not current_user.is_coach() and not current_user.is_admin()):
            flash('You do not have permission to access this page', 'danger')
            return redirect(url_for('core.home'))
        return f(*args, **kwargs)

    return decorated_function


@bp.route('/schedule')
@login_required
def schedule():
    # Get current date
    today = datetime.datetime.now().date()

    # Get upcoming matches
    upcoming_matches = Match.query.filter(Match.match_date >= today).order_by(Match.match_date).all()

    # Get past matches with results
    past_matches = Match.query.filter(Match.match_date < today).order_by(Match.match_date.desc()).all()

    return render_template('matches/schedule.html',
                           title='Match Schedule',
                           upcoming_matches=upcoming_matches,
                           past_matches=past_matches)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
@coach_or_admin_required
def create_match():
    form = MatchForm()
    if form.validate_on_submit():
        match = Match(
            opponent=form.opponent.data,
            match_date=form.match_date.data,
            location=form.location.data,
            is_home_game=form.is_home_game.data,
            notes=form.notes.data
        )
        db.session.add(match)
        db.session.commit()
        flash('Match added to schedule!', 'success')
        return redirect(url_for('matches.schedule'))

    return render_template('matches/create_match.html',
                           title='Schedule Match',
                           form=form)


@bp.route('/edit/<int:match_id>', methods=['GET', 'POST'])
@login_required
@coach_or_admin_required
def edit_match(match_id):
    match = Match.query.get_or_404(match_id)
    form = MatchForm(obj=match)

    if form.validate_on_submit():
        form.populate_obj(match)
        db.session.commit()
        flash('Match updated successfully!', 'success')
        return redirect(url_for('matches.schedule'))

    return render_template('matches/edit_match.html',
                           title='Edit Match',
                           form=form,
                           match=match)


@bp.route('/result/<int:match_id>', methods=['GET', 'POST'])
@login_required
@coach_or_admin_required
def update_result(match_id):
    match = Match.query.get_or_404(match_id)

    if request.method == 'POST':
        match.score_team = request.form.get('score_team', type=int)
        match.score_opponent = request.form.get('score_opponent', type=int)
        db.session.commit()
        flash('Match result updated!', 'success')
        return redirect(url_for('matches.schedule'))

    return render_template('matches/update_result.html',
                           title='Update Match Result',
                           match=match)