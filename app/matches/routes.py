from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.matches import bp
from app.matches.forms import MatchForm, GoalForm, CardForm
from app.models import Match, User, Goal, Card
from app.utils.decorators import coach_or_admin_required
import datetime


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
            match_type=form.match_type.data,
            tournament_name=form.tournament_name.data if form.tournament_name.data else None,
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
        return redirect(url_for('matches.match_details', match_id=match.id))

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
        return redirect(url_for('matches.match_details', match_id=match.id))

    return render_template('matches/update_result.html',
                           title='Update Match Result',
                           match=match)


@bp.route('/details/<int:match_id>')
@login_required
def match_details(match_id):
    match = Match.query.get_or_404(match_id)
    now = datetime.datetime.now()

    # Forms for adding stats
    goal_form = GoalForm()
    card_form = CardForm()

    # Populate player choices for both forms
    players = User.query.filter_by(role='player').all()
    goal_form.player_id.choices = [(p.id, p.username) for p in players]
    card_form.player_id.choices = [(p.id, p.username) for p in players]

    return render_template('matches/match_details.html',
                           title=f'Match vs {match.opponent}',
                           match=match,
                           now=now,
                           goal_form=goal_form,
                           card_form=card_form)


@bp.route('/goal/add/<int:match_id>', methods=['POST'])
@login_required
@coach_or_admin_required
def add_goal(match_id):
    match = Match.query.get_or_404(match_id)
    form = GoalForm()

    # Populate player choices
    players = User.query.filter_by(role='player').all()
    form.player_id.choices = [(p.id, p.username) for p in players]

    if form.validate_on_submit():
        goal = Goal(
            match_id=match.id,
            player_id=form.player_id.data,
            minute=form.minute.data,
            is_penalty=form.is_penalty.data,
            is_own_goal=form.is_own_goal.data
        )
        db.session.add(goal)
        db.session.commit()
        flash('Goal added successfully!', 'success')

    return redirect(url_for('matches.match_details', match_id=match.id))


@bp.route('/goal/delete/<int:goal_id>')
@login_required
@coach_or_admin_required
def delete_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    match_id = goal.match_id

    db.session.delete(goal)
    db.session.commit()
    flash('Goal deleted!', 'success')

    return redirect(url_for('matches.match_details', match_id=match_id))


@bp.route('/card/add/<int:match_id>', methods=['POST'])
@login_required
@coach_or_admin_required
def add_card(match_id):
    match = Match.query.get_or_404(match_id)
    form = CardForm()

    # Populate player choices
    players = User.query.filter_by(role='player').all()
    form.player_id.choices = [(p.id, p.username) for p in players]

    if form.validate_on_submit():
        card = Card(
            match_id=match.id,
            player_id=form.player_id.data,
            card_type=form.card_type.data,
            minute=form.minute.data,
            reason=form.reason.data
        )
        db.session.add(card)
        db.session.commit()
        flash('Card added successfully!', 'success')

    return redirect(url_for('matches.match_details', match_id=match.id))


@bp.route('/card/delete/<int:card_id>')
@login_required
@coach_or_admin_required
def delete_card(card_id):
    card = Card.query.get_or_404(card_id)
    match_id = card.match_id

    db.session.delete(card)
    db.session.commit()
    flash('Card deleted!', 'success')

    return redirect(url_for('matches.match_details', match_id=match_id))