# app/tournaments/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.tournaments.forms import TournamentForm
from app.models.tournament import Tournament
from app.models.event import Event
from app.extensions import db
from app.utils.decorators import admin_required
from datetime import datetime

tournaments = Blueprint('tournaments', __name__)


@tournaments.route('/')
def index():
    # Get all tournaments ordered by start date descending
    active_tournaments = Tournament.query.filter_by(is_active=True).order_by(Tournament.start_date.desc()).all()
    past_tournaments = Tournament.query.filter_by(is_active=False).order_by(Tournament.start_date.desc()).all()

    return render_template('tournaments/index.html',
                           title='Tournaments',
                           active_tournaments=active_tournaments,
                           past_tournaments=past_tournaments)


@tournaments.route('/detail/<int:tournament_id>')
def detail(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    events = Event.query.filter_by(tournament_id=tournament_id).order_by(Event.event_date).all()

    return render_template('tournaments/detail.html',
                           title=tournament.name,
                           tournament=tournament,
                           events=events)


@tournaments.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    form = TournamentForm()

    if form.validate_on_submit():
        tournament = Tournament(
            name=form.name.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            location=form.location.data,
            description=form.description.data,
            is_active=True
        )

        db.session.add(tournament)
        db.session.commit()

        flash('Tournament has been created!', 'success')
        return redirect(url_for('tournaments.index'))

    return render_template('tournaments/create.html', title='Create Tournament', form=form)


@tournaments.route('/update/<int:tournament_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def update(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    form = TournamentForm()

    if form.validate_on_submit():
        tournament.name = form.name.data
        tournament.start_date = form.start_date.data
        tournament.end_date = form.end_date.data
        tournament.location = form.location.data
        tournament.description = form.description.data

        db.session.commit()

        flash('Tournament has been updated!', 'success')
        return redirect(url_for('tournaments.detail', tournament_id=tournament.id))
    elif request.method == 'GET':
        form.name.data = tournament.name
        form.start_date.data = tournament.start_date
        form.end_date.data = tournament.end_date
        form.location.data = tournament.location
        form.description.data = tournament.description

    return render_template('tournaments/update.html',
                           title='Update Tournament',
                           form=form,
                           tournament=tournament)


@tournaments.route('/toggle_status/<int:tournament_id>', methods=['POST'])
@login_required
@admin_required
def toggle_status(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    tournament.is_active = not tournament.is_active

    db.session.commit()

    status = "activated" if tournament.is_active else "archived"
    flash(f'Tournament has been {status}!', 'success')
    return redirect(url_for('tournaments.detail', tournament_id=tournament.id))


@tournaments.route('/delete/<int:tournament_id>', methods=['POST'])
@login_required
@admin_required
def delete(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)

    # Check if tournament has events
    if tournament.events:
        flash('Cannot delete tournament with associated events. Remove events first or archive the tournament.',
              'danger')
        return redirect(url_for('tournaments.detail', tournament_id=tournament.id))

    db.session.delete(tournament)
    db.session.commit()

    flash('Tournament has been deleted!', 'success')
    return redirect(url_for('tournaments.index'))