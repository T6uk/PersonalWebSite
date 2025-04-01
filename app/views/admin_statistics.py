# app/views/admin_statistics.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from ..models.User import User
from ..models.Event import Event
from ..models.Statistics import (
    MatchStatistic, PlayerPerformance, TournamentStatistic, TournamentMatch
)
from ..forms.statistics_forms import (
    MatchStatisticForm, PlayerPerformanceForm, TournamentStatisticForm, TournamentMatchForm
)
from ..extensions import db
from datetime import datetime

admin_stats = Blueprint('admin_stats', __name__, url_prefix='/admin/statistics')


# Decorator to check if user is admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('You need to be an admin to access this page.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)

    return decorated_function


@admin_stats.route('/event/<int:event_id>')
@login_required
@admin_required
def event_statistics(event_id):
    event = Event.query.get_or_404(event_id)

    if event.event_type == 'league_game' or event.event_type == 'friendly_match':
        match_stats = MatchStatistic.query.filter_by(event_id=event.id).first()
        if match_stats:
            player_performances = PlayerPerformance.query.filter_by(match_id=match_stats.id).all()
            return render_template('admin/statistics/match_statistics.html',
                                   event=event,
                                   match_stats=match_stats,
                                   player_performances=player_performances)
        else:
            return redirect(url_for('admin_stats.add_match_statistics', event_id=event.id))

    elif event.event_type == 'tournament':
        tournament_stats = TournamentStatistic.query.filter_by(event_id=event.id).first()
        if tournament_stats:
            tournament_matches = TournamentMatch.query.filter_by(tournament_id=tournament_stats.id).all()
            return render_template('admin/statistics/tournament_statistics.html',
                                   event=event,
                                   tournament_stats=tournament_stats,
                                   tournament_matches=tournament_matches)
        else:
            return redirect(url_for('admin_stats.add_tournament_statistics', event_id=event.id))

    else:
        flash('Statistics are not available for this event type.', 'info')
        return redirect(url_for('admin.manage_events'))


@admin_stats.route('/match/<int:event_id>/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_match_statistics(event_id):
    event = Event.query.get_or_404(event_id)

    if event.event_type not in ['league_game', 'friendly_match']:
        flash('You can only add match statistics to league games or friendly matches.', 'danger')
        return redirect(url_for('admin.manage_events'))

    form = MatchStatisticForm()

    if form.validate_on_submit():
        match_stats = MatchStatistic(
            event_id=event.id,
            home_team=form.home_team.data,
            away_team=form.away_team.data,
            home_score=form.home_score.data,
            away_score=form.away_score.data,
            match_date=form.match_date.data,
            location=form.location.data,
            referee=form.referee.data,
            attendance=form.attendance.data,
            notes=form.notes.data,
            created_by_id=current_user.id
        )

        db.session.add(match_stats)

        # Update event statistics flag
        event.has_statistics = True
        event.statistics_last_updated = datetime.utcnow()

        db.session.commit()

        flash('Match statistics added successfully!', 'success')
        return redirect(url_for('admin_stats.add_player_performance', match_id=match_stats.id))

    # Pre-populate the form with event data
    if request.method == 'GET':
        form.match_date.data = event.start_datetime
        form.location.data = event.location

    return render_template('admin/statistics/add_match_statistics.html',
                           title='Add Match Statistics',
                           form=form,
                           event=event)


@admin_stats.route('/match/<int:match_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_match_statistics(match_id):
    match_stats = MatchStatistic.query.get_or_404(match_id)
    event = Event.query.get_or_404(match_stats.event_id)

    form = MatchStatisticForm()

    if form.validate_on_submit():
        match_stats.home_team = form.home_team.data
        match_stats.away_team = form.away_team.data
        match_stats.home_score = form.home_score.data
        match_stats.away_score = form.away_score.data
        match_stats.match_date = form.match_date.data
        match_stats.location = form.location.data
        match_stats.referee = form.referee.data
        match_stats.attendance = form.attendance.data
        match_stats.notes = form.notes.data

        # Update event statistics timestamp
        event.statistics_last_updated = datetime.utcnow()

        db.session.commit()

        flash('Match statistics updated successfully!', 'success')
        return redirect(url_for('admin_stats.event_statistics', event_id=event.id))

    elif request.method == 'GET':
        form.home_team.data = match_stats.home_team
        form.away_team.data = match_stats.away_team
        form.home_score.data = match_stats.home_score
        form.away_score.data = match_stats.away_score
        form.match_date.data = match_stats.match_date
        form.location.data = match_stats.location
        form.referee.data = match_stats.referee
        form.attendance.data = match_stats.attendance
        form.notes.data = match_stats.notes

    return render_template('admin/statistics/edit_match_statistics.html',
                           title='Edit Match Statistics',
                           form=form,
                           match_stats=match_stats,
                           event=event)


@admin_stats.route('/performance/<int:match_id>/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_player_performance(match_id):
    match_stats = MatchStatistic.query.get_or_404(match_id)
    event = Event.query.get_or_404(match_stats.event_id)

    form = PlayerPerformanceForm()

    # Get players for the dropdown
    players = User.query.filter_by(role='player').all()
    form.player_id.choices = [(player.id, f"{player.username} (#{player.jersey_number})") for player in players]

    if form.validate_on_submit():
        # Check if performance already exists for this player and match
        existing_performance = PlayerPerformance.query.filter_by(
            match_id=match_id,
            player_id=form.player_id.data
        ).first()

        if existing_performance:
            flash(f'Performance for this player already exists! You can edit it instead.', 'warning')
            return redirect(url_for('admin_stats.edit_player_performance', performance_id=existing_performance.id))

        performance = PlayerPerformance(
            match_id=match_id,
            player_id=form.player_id.data,
            minutes_played=form.minutes_played.data,
            goals=form.goals.data,
            assists=form.assists.data,
            yellow_cards=form.yellow_cards.data,
            red_cards=form.red_cards.data,
            passes_completed=form.passes_completed.data,
            pass_accuracy=form.pass_accuracy.data,
            shots=form.shots.data,
            shots_on_target=form.shots_on_target.data,
            dribbles_completed=form.dribbles_completed.data,
            tackles=form.tackles.data,
            interceptions=form.interceptions.data,
            clearances=form.clearances.data,
            blocks=form.blocks.data,
            saves=form.saves.data,
            goals_conceded=form.goals_conceded.data,
            rating=form.rating.data,
            notes=form.notes.data
        )

        db.session.add(performance)

        # Update event statistics timestamp
        event.statistics_last_updated = datetime.utcnow()

        db.session.commit()
        flash('Player performance has been added successfully!', 'success')

        # Offer to add another player or return to match statistics
        return render_template('admin/statistics/performance_added.html',
                               match_stats=match_stats,
                               event=event)

    return render_template('admin/statistics/add_player_performance.html',
                           title='Add Player Performance',
                           form=form,
                           match_stats=match_stats,
                           event=event)

    @admin_stats.route('/performance/<int:performance_id>/edit', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def edit_player_performance(performance_id):
        performance = PlayerPerformance.query.get_or_404(performance_id)
        match_stats = MatchStatistic.query.get_or_404(performance.match_id)
        event = Event.query.get_or_404(match_stats.event_id)

        form = PlayerPerformanceForm()

        # Get players for the dropdown
        players = User.query.filter_by(role='player').all()
        form.player_id.choices = [(player.id, f"{player.username} (#{player.jersey_number})") for player in players]

        if form.validate_on_submit():
            performance.minutes_played = form.minutes_played.data
            performance.goals = form.goals.data
            performance.assists = form.assists.data
            performance.yellow_cards = form.yellow_cards.data
            performance.red_cards = form.red_cards.data
            performance.passes_completed = form.passes_completed.data
            performance.pass_accuracy = form.pass_accuracy.data
            performance.shots = form.shots.data
            performance.shots_on_target = form.shots_on_target.data
            performance.dribbles_completed = form.dribbles_completed.data
            performance.tackles = form.tackles.data
            performance.interceptions = form.interceptions.data
            performance.clearances = form.clearances.data
            performance.blocks = form.blocks.data
            performance.saves = form.saves.data
            performance.goals_conceded = form.goals_conceded.data
            performance.rating = form.rating.data
            performance.notes = form.notes.data

            # Update event statistics timestamp
            event.statistics_last_updated = datetime.utcnow()

            db.session.commit()

            flash('Player performance has been updated successfully!', 'success')
            return redirect(url_for('admin_stats.event_statistics', event_id=event.id))

        elif request.method == 'GET':
            form.player_id.data = performance.player_id
            form.minutes_played.data = performance.minutes_played
            form.goals.data = performance.goals
            form.assists.data = performance.assists
            form.yellow_cards.data = performance.yellow_cards
            form.red_cards.data = performance.red_cards
            form.passes_completed.data = performance.passes_completed
            form.pass_accuracy.data = performance.pass_accuracy
            form.shots.data = performance.shots
            form.shots_on_target.data = performance.shots_on_target
            form.dribbles_completed.data = performance.dribbles_completed
            form.tackles.data = performance.tackles
            form.interceptions.data = performance.interceptions
            form.clearances.data = performance.clearances
            form.blocks.data = performance.blocks
            form.saves.data = performance.saves
            form.goals_conceded.data = performance.goals_conceded
            form.rating.data = performance.rating
            form.notes.data = performance.notes

        return render_template('admin/statistics/edit_player_performance.html',
                               title='Edit Player Performance',
                               form=form,
                               performance=performance,
                               match_stats=match_stats,
                               event=event)

    @admin_stats.route('/performance/<int:performance_id>/delete', methods=['POST'])
    @login_required
    @admin_required
    def delete_player_performance(performance_id):
        performance = PlayerPerformance.query.get_or_404(performance_id)
        match_id = performance.match_id
        match_stats = MatchStatistic.query.get_or_404(match_id)
        event = Event.query.get_or_404(match_stats.event_id)

        player_name = performance.player.username

        db.session.delete(performance)
        event.statistics_last_updated = datetime.utcnow()
        db.session.commit()

        flash(f'Performance record for {player_name} has been deleted.', 'success')
        return redirect(url_for('admin_stats.event_statistics', event_id=event.id))

    @admin_stats.route('/tournament/<int:event_id>/add', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def add_tournament_statistics(event_id):
        event = Event.query.get_or_404(event_id)

        if event.event_type != 'tournament':
            flash('You can only add tournament statistics to tournament events.', 'danger')
            return redirect(url_for('admin.manage_events'))

        form = TournamentStatisticForm()

        if form.validate_on_submit():
            tournament_stats = TournamentStatistic(
                event_id=event.id,
                tournament_name=form.tournament_name.data,
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                position=form.position.data,
                matches_played=form.matches_played.data,
                wins=form.wins.data,
                draws=form.draws.data,
                losses=form.losses.data,
                goals_for=form.goals_for.data,
                goals_against=form.goals_against.data,
                location=form.location.data,
                notes=form.notes.data,
                created_by_id=current_user.id
            )

            db.session.add(tournament_stats)

            # Update event statistics flag
            event.has_statistics = True
            event.statistics_last_updated = datetime.utcnow()

            db.session.commit()

            flash('Tournament statistics added successfully!', 'success')
            return redirect(url_for('admin_stats.add_tournament_match', tournament_id=tournament_stats.id))

        # Pre-populate the form with event data
        if request.method == 'GET':
            form.tournament_name.data = event.title
            form.start_date.data = event.start_datetime
            form.end_date.data = event.end_datetime
            form.location.data = event.location

        return render_template('admin/statistics/add_tournament_statistics.html',
                               title='Add Tournament Statistics',
                               form=form,
                               event=event)

    @admin_stats.route('/tournament/<int:tournament_id>/edit', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def edit_tournament_statistics(tournament_id):
        tournament_stats = TournamentStatistic.query.get_or_404(tournament_id)
        event = Event.query.get_or_404(tournament_stats.event_id)

        form = TournamentStatisticForm()

        if form.validate_on_submit():
            tournament_stats.tournament_name = form.tournament_name.data
            tournament_stats.start_date = form.start_date.data
            tournament_stats.end_date = form.end_date.data
            tournament_stats.position = form.position.data
            tournament_stats.matches_played = form.matches_played.data
            tournament_stats.wins = form.wins.data
            tournament_stats.draws = form.draws.data
            tournament_stats.losses = form.losses.data
            tournament_stats.goals_for = form.goals_for.data
            tournament_stats.goals_against = form.goals_against.data
            tournament_stats.location = form.location.data
            tournament_stats.notes = form.notes.data

            # Update event statistics timestamp
            event.statistics_last_updated = datetime.utcnow()

            db.session.commit()

            flash('Tournament statistics updated successfully!', 'success')
            return redirect(url_for('admin_stats.event_statistics', event_id=event.id))

        elif request.method == 'GET':
            form.tournament_name.data = tournament_stats.tournament_name
            form.start_date.data = tournament_stats.start_date
            form.end_date.data = tournament_stats.end_date
            form.position.data = tournament_stats.position
            form.matches_played.data = tournament_stats.matches_played
            form.wins.data = tournament_stats.wins
            form.draws.data = tournament_stats.draws
            form.losses.data = tournament_stats.losses
            form.goals_for.data = tournament_stats.goals_for
            form.goals_against.data = tournament_stats.goals_against
            form.location.data = tournament_stats.location
            form.notes.data = tournament_stats.notes

        return render_template('admin/statistics/edit_tournament_statistics.html',
                               title='Edit Tournament Statistics',
                               form=form,
                               tournament_stats=tournament_stats,
                               event=event)

    @admin_stats.route('/tournament/<int:tournament_id>/match/add', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def add_tournament_match(tournament_id):
        tournament_stats = TournamentStatistic.query.get_or_404(tournament_id)
        event = Event.query.get_or_404(tournament_stats.event_id)

        form = TournamentMatchForm()

        if form.validate_on_submit():
            tournament_match = TournamentMatch(
                tournament_id=tournament_id,
                match_round=form.match_round.data,
                home_team=form.home_team.data,
                away_team=form.away_team.data,
                home_score=form.home_score.data,
                away_score=form.away_score.data,
                match_date=form.match_date.data,
                location=form.location.data,
                notes=form.notes.data
            )

            db.session.add(tournament_match)

            # Update event statistics timestamp
            event.statistics_last_updated = datetime.utcnow()

            db.session.commit()

            flash('Tournament match added successfully!', 'success')

            # Offer to add another match or return to tournament statistics
            return render_template('admin/statistics/match_added.html',
                                   tournament_stats=tournament_stats,
                                   event=event)

        # Pre-populate form with FC Mara as one of the teams
        if request.method == 'GET':
            form.home_team.data = 'FC Mara'
            form.match_date.data = tournament_stats.start_date

        return render_template('admin/statistics/add_tournament_match.html',
                               title='Add Tournament Match',
                               form=form,
                               tournament_stats=tournament_stats,
                               event=event)

    @admin_stats.route('/tournament/match/<int:match_id>/edit', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def edit_tournament_match(match_id):
        tournament_match = TournamentMatch.query.get_or_404(match_id)
        tournament_stats = TournamentStatistic.query.get_or_404(tournament_match.tournament_id)
        event = Event.query.get_or_404(tournament_stats.event_id)

        form = TournamentMatchForm()

        if form.validate_on_submit():
            tournament_match.match_round = form.match_round.data
            tournament_match.home_team = form.home_team.data
            tournament_match.away_team = form.away_team.data
            tournament_match.home_score = form.home_score.data
            tournament_match.away_score = form.away_score.data
            tournament_match.match_date = form.match_date.data
            tournament_match.location = form.location.data
            tournament_match.notes = form.notes.data

            # Update event statistics timestamp
            event.statistics_last_updated = datetime.utcnow()

            db.session.commit()

            flash('Tournament match updated successfully!', 'success')
            return redirect(url_for('admin_stats.event_statistics', event_id=event.id))

        elif request.method == 'GET':
            form.match_round.data = tournament_match.match_round
            form.home_team.data = tournament_match.home_team
            form.away_team.data = tournament_match.away_team
            form.home_score.data = tournament_match.home_score
            form.away_score.data = tournament_match.away_score
            form.match_date.data = tournament_match.match_date
            form.location.data = tournament_match.location
            form.notes.data = tournament_match.notes

        return render_template('admin/statistics/edit_tournament_match.html',
                               title='Edit Tournament Match',
                               form=form,
                               tournament_match=tournament_match,
                               tournament_stats=tournament_stats,
                               event=event)

    @admin_stats.route('/tournament/match/<int:match_id>/delete', methods=['POST'])
    @login_required
    @admin_required
    def delete_tournament_match(match_id):
        tournament_match = TournamentMatch.query.get_or_404(match_id)
        tournament_id = tournament_match.tournament_id
        tournament_stats = TournamentStatistic.query.get_or_404(tournament_id)
        event = Event.query.get_or_404(tournament_stats.event_id)

        match_info = f"{tournament_match.home_team} vs {tournament_match.away_team}"

        db.session.delete(tournament_match)
        event.statistics_last_updated = datetime.utcnow()
        db.session.commit()

        flash(f'Tournament match {match_info} has been deleted.', 'success')
        return redirect(url_for('admin_stats.event_statistics', event_id=event.id))

    @admin_stats.route('/player/<int:player_id>')
    @login_required
    @admin_required
    def player_statistics(player_id):
        player = User.query.get_or_404(player_id)

        if not player.is_player():
            flash('Statistics are only available for players.', 'warning')
            return redirect(url_for('admin.manage_players'))

        # Get current season
        current_year = datetime.utcnow().year
        current_month = datetime.utcnow().month
        if current_month >= 8:  # If after August, use current season format (e.g., 2024-2025)
            current_season = f"{current_year}-{current_year + 1}"
        else:  # If before August, use previous season format
            current_season = f"{current_year - 1}-{current_year}"

        # Get season statistics
        season_stats = player.get_season_statistics(season=current_season)

        # Get statistics by event type
        league_stats = player.get_event_type_statistics('league_game', season=current_season)
        friendly_stats = player.get_event_type_statistics('friendly_match', season=current_season)
        tournament_stats = player.get_event_type_statistics('tournament', season=current_season)

        # Get recent performances
        recent_performances = player.get_recent_performances(limit=5)

        return render_template('admin/statistics/player_statistics.html',
                               player=player,
                               current_season=current_season,
                               season_stats=season_stats,
                               league_stats=league_stats,
                               friendly_stats=friendly_stats,
                               tournament_stats=tournament_stats,
                               recent_performances=recent_performances)
