from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.statistics.forms import TeamStatisticForm, PlayerStatisticForm
from app.models.statistic import TeamStatistic, PlayerStatistic
from app.models.user import User
from app.extensions import db
from app.utils.decorators import admin_required

statistics = Blueprint('statistics', __name__)


@statistics.route('/')
def index():
    # Get latest team statistics
    team_stats = TeamStatistic.query.order_by(TeamStatistic.season.desc()).first()

    # Get top players by goals
    top_scorers = db.session.query(
        User, db.func.sum(PlayerStatistic.goals).label('total_goals')
    ).join(PlayerStatistic).group_by(User.id).order_by(db.desc('total_goals')).limit(5).all()

    # Get all seasons
    seasons = db.session.query(TeamStatistic.season).distinct().order_by(TeamStatistic.season.desc()).all()

    return render_template('statistics/index.html',
                           title='Statistics',
                           team_stats=team_stats,
                           top_scorers=top_scorers,
                           seasons=seasons)


@statistics.route('/team')
def team():
    season = request.args.get('season', None)

    if season:
        team_stats = TeamStatistic.query.filter_by(season=season).first_or_404()
    else:
        team_stats = TeamStatistic.query.order_by(TeamStatistic.season.desc()).first_or_404()

    seasons = db.session.query(TeamStatistic.season).distinct().order_by(TeamStatistic.season.desc()).all()

    return render_template('statistics/team.html',
                           title='Team Statistics',
                           team_stats=team_stats,
                           seasons=seasons,
                           current_season=season or team_stats.season)


@statistics.route('/players')
def players():
    season = request.args.get('season', None)

    if season:
        player_stats = PlayerStatistic.query.filter_by(season=season).all()
    else:
        # Get most recent season
        latest_season = db.session.query(PlayerStatistic.season).order_by(PlayerStatistic.season.desc()).first()
        if latest_season:
            season = latest_season[0]
            player_stats = PlayerStatistic.query.filter_by(season=season).all()
        else:
            player_stats = []

    seasons = db.session.query(PlayerStatistic.season).distinct().order_by(PlayerStatistic.season.desc()).all()

    return render_template('statistics/players.html',
                           title='Player Statistics',
                           player_stats=player_stats,
                           seasons=seasons,
                           current_season=season)


@statistics.route('/player/<int:player_id>')
def player_detail(player_id):
    player = User.query.get_or_404(player_id)
    stats = PlayerStatistic.query.filter_by(player_id=player_id).order_by(PlayerStatistic.season.desc()).all()

    # Calculate career totals
    career_totals = {
        'appearances': sum(stat.appearances for stat in stats),
        'goals': sum(stat.goals for stat in stats),
        'assists': sum(stat.assists for stat in stats),
        'yellow_cards': sum(stat.yellow_cards for stat in stats),
        'red_cards': sum(stat.red_cards for stat in stats),
        'minutes_played': sum(stat.minutes_played for stat in stats)
    }

    return render_template('statistics/player_detail.html',
                           title=f"{player.first_name} {player.last_name} - Statistics",
                           player=player,
                           stats=stats,
                           career_totals=career_totals)


@statistics.route('/team/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_team_stat():
    form = TeamStatisticForm()

    if form.validate_on_submit():
        # Check if statistics for this season already exists
        existing = TeamStatistic.query.filter_by(season=form.season.data).first()
        if existing:
            flash(f'Team statistics for season {form.season.data} already exists. Please update instead.', 'danger')
            return redirect(url_for('statistics.team'))

        team_stat = TeamStatistic(
            season=form.season.data,
            wins=form.wins.data,
            losses=form.losses.data,
            draws=form.draws.data,
            goals_scored=form.goals_scored.data,
            goals_conceded=form.goals_conceded.data,
            clean_sheets=form.clean_sheets.data,
            league_position=form.league_position.data
        )

        db.session.add(team_stat)
        db.session.commit()

        flash('Team statistics have been created!', 'success')
        return redirect(url_for('statistics.team'))

    return render_template('statistics/create_team_stat.html', title='Create Team Statistics', form=form)


@statistics.route('/team/update/<int:stat_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def update_team_stat(stat_id):
    team_stat = TeamStatistic.query.get_or_404(stat_id)
    form = TeamStatisticForm()

    if form.validate_on_submit():
        team_stat.season = form.season.data
        team_stat.wins = form.wins.data
        team_stat.losses = form.losses.data
        team_stat.draws = form.draws.data
        team_stat.goals_scored = form.goals_scored.data
        team_stat.goals_conceded = form.goals_conceded.data
        team_stat.clean_sheets = form.clean_sheets.data
        team_stat.league_position = form.league_position.data

        db.session.commit()

        flash('Team statistics have been updated!', 'success')
        return redirect(url_for('statistics.team'))
    elif request.method == 'GET':
        form.season.data = team_stat.season
        form.wins.data = team_stat.wins
        form.losses.data = team_stat.losses
        form.draws.data = team_stat.draws
        form.goals_scored.data = team_stat.goals_scored
        form.goals_conceded.data = team_stat.goals_conceded
        form.clean_sheets.data = team_stat.clean_sheets
        form.league_position.data = team_stat.league_position

    return render_template('statistics/update_team_stat.html',
                           title='Update Team Statistics',
                           form=form,
                           team_stat=team_stat)


@statistics.route('/team/delete/<int:stat_id>', methods=['POST'])
@login_required
@admin_required
def delete_team_stat(stat_id):
    team_stat = TeamStatistic.query.get_or_404(stat_id)

    db.session.delete(team_stat)
    db.session.commit()

    flash('Team statistics have been deleted!', 'success')
    return redirect(url_for('statistics.team'))


@statistics.route('/player/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_player_stat():
    form = PlayerStatisticForm()

    if form.validate_on_submit():
        # Check if statistics for this player and season already exists
        existing = PlayerStatistic.query.filter_by(
            player_id=form.player.data,
            season=form.season.data
        ).first()

        if existing:
            flash(f'Statistics for this player and season already exist. Please update instead.', 'danger')
            return redirect(url_for('statistics.players'))

        player_stat = PlayerStatistic(
            player_id=form.player.data,
            season=form.season.data,
            appearances=form.appearances.data,
            goals=form.goals.data,
            assists=form.assists.data,
            yellow_cards=form.yellow_cards.data,
            red_cards=form.red_cards.data,
            minutes_played=form.minutes_played.data
        )

        db.session.add(player_stat)
        db.session.commit()

        flash('Player statistics have been created!', 'success')
        return redirect(url_for('statistics.players'))

    return render_template('statistics/create_player_stat.html', title='Create Player Statistics', form=form)


@statistics.route('/player/update/<int:stat_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def update_player_stat(stat_id):
    player_stat = PlayerStatistic.query.get_or_404(stat_id)
    form = PlayerStatisticForm()

    if form.validate_on_submit():
        player_stat.player_id = form.player.data
        player_stat.season = form.season.data
        player_stat.appearances = form.appearances.data
        player_stat.goals = form.goals.data
        player_stat.assists = form.assists.data
        player_stat.yellow_cards = form.yellow_cards.data
        player_stat.red_cards = form.red_cards.data
        player_stat.minutes_played = form.minutes_played.data

        db.session.commit()

        flash('Player statistics have been updated!', 'success')
        return redirect(url_for('statistics.player_detail', player_id=player_stat.player_id))
    elif request.method == 'GET':
        form.player.data = player_stat.player_id
        form.season.data = player_stat.season
        form.appearances.data = player_stat.appearances
        form.goals.data = player_stat.goals
        form.assists.data = player_stat.assists
        form.yellow_cards.data = player_stat.yellow_cards
        form.red_cards.data = player_stat.red_cards
        form.minutes_played.data = player_stat.minutes_played

    return render_template('statistics/update_player_stat.html',
                           title='Update Player Statistics',
                           form=form,
                           player_stat=player_stat)


@statistics.route('/player/delete/<int:stat_id>', methods=['POST'])
@login_required
@admin_required
def delete_player_stat(stat_id):
    player_stat = PlayerStatistic.query.get_or_404(stat_id)
    player_id = player_stat.player_id

    db.session.delete(player_stat)
    db.session.commit()

    flash('Player statistics have been deleted!', 'success')
    return redirect(url_for('statistics.player_detail', player_id=player_id))
