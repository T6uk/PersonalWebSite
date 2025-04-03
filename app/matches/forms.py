from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, DateTimeField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from app.models import MatchType


class MatchForm(FlaskForm):
    opponent = StringField('Opponent Team', validators=[DataRequired(), Length(min=2, max=100)])
    match_date = DateTimeField('Match Date & Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired(), Length(min=2, max=100)])
    is_home_game = BooleanField('Home Game')
    match_type = SelectField('Match Type', choices=[
        (MatchType.FRIENDLY, 'Friendly'),
        (MatchType.LEAGUE, 'League'),
        (MatchType.TOURNAMENT, 'Tournament'),
        (MatchType.CUP, 'Cup')
    ], validators=[DataRequired()])
    tournament_name = StringField('Tournament/League Name', validators=[Optional(), Length(max=100)])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Save Match')


class GoalForm(FlaskForm):
    player_id = SelectField('Player', coerce=int, validators=[DataRequired()])
    minute = StringField('Minute', validators=[DataRequired()])
    is_penalty = BooleanField('Penalty')
    is_own_goal = BooleanField('Own Goal')
    submit = SubmitField('Add Goal')


class CardForm(FlaskForm):
    player_id = SelectField('Player', coerce=int, validators=[DataRequired()])
    card_type = SelectField('Card Type', choices=[
        ('yellow', 'Yellow Card'),
        ('red', 'Red Card')
    ], validators=[DataRequired()])
    minute = StringField('Minute', validators=[DataRequired()])
    reason = StringField('Reason', validators=[Optional(), Length(max=200)])
    submit = SubmitField('Add Card')
