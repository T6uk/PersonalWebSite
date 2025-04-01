# app/forms/statistics_forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateTimeLocalField, SubmitField, IntegerField, FloatField
from wtforms.validators import DataRequired, Length, Optional, NumberRange


class MatchStatisticForm(FlaskForm):
    home_team = StringField('Home Team', validators=[DataRequired(), Length(max=100)], default='FC Mara')
    away_team = StringField('Away Team', validators=[DataRequired(), Length(max=100)])
    home_score = IntegerField('Home Score', validators=[NumberRange(min=0)], default=0)
    away_score = IntegerField('Away Score', validators=[NumberRange(min=0)], default=0)
    match_date = DateTimeLocalField('Match Date & Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    location = StringField('Location', validators=[Optional(), Length(max=100)])
    referee = StringField('Referee', validators=[Optional(), Length(max=100)])
    attendance = IntegerField('Attendance', validators=[Optional(), NumberRange(min=0)])
    notes = TextAreaField('Match Notes', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Save Match Statistics')


class PlayerPerformanceForm(FlaskForm):
    player_id = SelectField('Player', coerce=int, validators=[DataRequired()])
    minutes_played = IntegerField('Minutes Played', validators=[NumberRange(min=0, max=120)], default=0)
    goals = IntegerField('Goals', validators=[NumberRange(min=0)], default=0)
    assists = IntegerField('Assists', validators=[NumberRange(min=0)], default=0)
    yellow_cards = IntegerField('Yellow Cards', validators=[NumberRange(min=0, max=2)], default=0)
    red_cards = IntegerField('Red Cards', validators=[NumberRange(min=0, max=1)], default=0)

    # Position-specific stats with conditional validation
    passes_completed = IntegerField('Passes Completed', validators=[Optional(), NumberRange(min=0)], default=0)
    pass_accuracy = FloatField('Pass Accuracy (%)', validators=[Optional(), NumberRange(min=0, max=100)], default=0)
    shots = IntegerField('Shots', validators=[Optional(), NumberRange(min=0)], default=0)
    shots_on_target = IntegerField('Shots on Target', validators=[Optional(), NumberRange(min=0)], default=0)
    dribbles_completed = IntegerField('Successful Dribbles', validators=[Optional(), NumberRange(min=0)], default=0)
    tackles = IntegerField('Tackles', validators=[Optional(), NumberRange(min=0)], default=0)
    interceptions = IntegerField('Interceptions', validators=[Optional(), NumberRange(min=0)], default=0)
    clearances = IntegerField('Clearances', validators=[Optional(), NumberRange(min=0)], default=0)
    blocks = IntegerField('Blocks', validators=[Optional(), NumberRange(min=0)], default=0)
    saves = IntegerField('Saves', validators=[Optional(), NumberRange(min=0)], default=0)
    goals_conceded = IntegerField('Goals Conceded', validators=[Optional(), NumberRange(min=0)], default=0)

    rating = FloatField('Player Rating (1-10)', validators=[NumberRange(min=1, max=10)], default=6.0)
    notes = TextAreaField('Performance Notes', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Save Player Performance')


class TournamentStatisticForm(FlaskForm):
    tournament_name = StringField('Tournament Name', validators=[DataRequired(), Length(max=100)])
    start_date = DateTimeLocalField('Start Date', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    end_date = DateTimeLocalField('End Date', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    position = IntegerField('Final Position', validators=[Optional(), NumberRange(min=1)])
    matches_played = IntegerField('Matches Played', validators=[NumberRange(min=0)], default=0)
    wins = IntegerField('Wins', validators=[NumberRange(min=0)], default=0)
    draws = IntegerField('Draws', validators=[NumberRange(min=0)], default=0)
    losses = IntegerField('Losses', validators=[NumberRange(min=0)], default=0)
    goals_for = IntegerField('Goals For', validators=[NumberRange(min=0)], default=0)
    goals_against = IntegerField('Goals Against', validators=[NumberRange(min=0)], default=0)
    location = StringField('Tournament Location', validators=[Optional(), Length(max=100)])
    notes = TextAreaField('Tournament Notes', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Save Tournament Statistics')


class TournamentMatchForm(FlaskForm):
    match_round = SelectField('Round', choices=[
        ('Group Stage', 'Group Stage'),
        ('Round of 16', 'Round of 16'),
        ('Quarterfinal', 'Quarterfinal'),
        ('Semifinal', 'Semifinal'),
        ('Third Place', 'Third Place'),
        ('Final', 'Final'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    home_team = StringField('Home Team', validators=[DataRequired(), Length(max=100)])
    away_team = StringField('Away Team', validators=[DataRequired(), Length(max=100)])
    home_score = IntegerField('Home Score', validators=[NumberRange(min=0)], default=0)
    away_score = IntegerField('Away Score', validators=[NumberRange(min=0)], default=0)
    match_date = DateTimeLocalField('Match Date & Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    location = StringField('Location', validators=[Optional(), Length(max=100)])
    notes = TextAreaField('Match Notes', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Save Tournament Match')