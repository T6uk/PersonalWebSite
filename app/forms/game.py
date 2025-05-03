from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateTimeField, TextAreaField, BooleanField
from wtforms import IntegerField, SubmitField, FormField, FieldList, Form, FloatField
from wtforms.validators import DataRequired, Optional, NumberRange, Length, URL
from wtforms.fields import DateTimeLocalField

class GameForm(FlaskForm):
    event_id = SelectField('Event', coerce=int, validators=[DataRequired()])
    opponent = StringField('Opponent', validators=[DataRequired(), Length(max=128)])
    date = DateTimeLocalField('Date and Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    location = StringField('Location', validators=[Optional(), Length(max=128)])
    is_home_game = BooleanField('Home Game', default=True)
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save Game')


class GameResultForm(FlaskForm):
    score_team = IntegerField('Team Score', validators=[DataRequired(), NumberRange(min=0)])
    score_opponent = IntegerField('Opponent Score', validators=[DataRequired(), NumberRange(min=0)])
    status = SelectField('Status',
                       choices=[('completed', 'Completed'),
                                ('cancelled', 'Cancelled')],
                       validators=[DataRequired()])
    highlights_url = StringField('Highlights URL', validators=[Optional(), URL()])
    notes = TextAreaField('Match Notes', validators=[Optional()])
    submit = SubmitField('Save Result')


class PlayerStatForm(Form):
    player_id = SelectField('Player', coerce=int, validators=[DataRequired()])
    goals = IntegerField('Goals', default=0, validators=[NumberRange(min=0)])
    assists = IntegerField('Assists', default=0, validators=[NumberRange(min=0)])
    minutes_played = IntegerField('Minutes Played', default=0, validators=[NumberRange(min=0, max=120)])
    yellow_cards = IntegerField('Yellow Cards', default=0, validators=[NumberRange(min=0, max=2)])
    red_cards = IntegerField('Red Cards', default=0, validators=[NumberRange(min=0, max=1)])
    shots = IntegerField('Shots', default=0, validators=[Optional(), NumberRange(min=0)])
    shots_on_target = IntegerField('Shots on Target', default=0, validators=[Optional(), NumberRange(min=0)])
    rating = FloatField('Player Rating (1-10)', validators=[Optional(), NumberRange(min=1, max=10)])
    notes = TextAreaField('Notes', validators=[Optional()])


class GameStatsForm(FlaskForm):
    player_stats = FieldList(FormField(PlayerStatForm), min_entries=1)
    submit = SubmitField('Save Player Statistics')