from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class TeamStatisticForm(FlaskForm):
    season = StringField('Season', validators=[DataRequired()])
    wins = IntegerField('Wins', validators=[NumberRange(min=0)], default=0)
    losses = IntegerField('Losses', validators=[NumberRange(min=0)], default=0)
    draws = IntegerField('Draws', validators=[NumberRange(min=0)], default=0)
    goals_scored = IntegerField('Goals Scored', validators=[NumberRange(min=0)], default=0)
    goals_conceded = IntegerField('Goals Conceded', validators=[NumberRange(min=0)], default=0)
    clean_sheets = IntegerField('Clean Sheets', validators=[NumberRange(min=0)], default=0)
    league_position = IntegerField('League Position', validators=[NumberRange(min=1)], default=1)
    submit = SubmitField('Save')


class PlayerStatisticForm(FlaskForm):
    player = SelectField('Player', coerce=int, validators=[DataRequired()])
    season = StringField('Season', validators=[DataRequired()])
    appearances = IntegerField('Appearances', validators=[NumberRange(min=0)], default=0)
    goals = IntegerField('Goals', validators=[NumberRange(min=0)], default=0)
    assists = IntegerField('Assists', validators=[NumberRange(min=0)], default=0)
    yellow_cards = IntegerField('Yellow Cards', validators=[NumberRange(min=0)], default=0)
    red_cards = IntegerField('Red Cards', validators=[NumberRange(min=0)], default=0)
    minutes_played = IntegerField('Minutes Played', validators=[NumberRange(min=0)], default=0)
    submit = SubmitField('Save')

    def __init__(self, *args, **kwargs):
        super(PlayerStatisticForm, self).__init__(*args, **kwargs)
        from app.models.user import User
        self.player.choices = [(u.id, f"{u.first_name} {u.last_name}")
                               for u in User.query.filter_by(user_type='player').order_by('last_name')]
