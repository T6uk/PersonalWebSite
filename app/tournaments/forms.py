# app/tournaments/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeLocalField, SubmitField
from wtforms.validators import DataRequired, Length

class TournamentForm(FlaskForm):
    name = StringField('Tournament Name', validators=[DataRequired(), Length(max=120)])
    start_date = DateTimeLocalField('Start Date', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    end_date = DateTimeLocalField('End Date', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    location = StringField('Location', validators=[Length(max=120)])
    description = TextAreaField('Description')
    submit = SubmitField('Save')