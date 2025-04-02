from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, DateTimeField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class MatchForm(FlaskForm):
    opponent = StringField('Opponent Team', validators=[DataRequired(), Length(min=2, max=100)])
    match_date = DateTimeField('Match Date & Time', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired(), Length(min=2, max=100)])
    is_home_game = BooleanField('Home Game')
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Save Match')