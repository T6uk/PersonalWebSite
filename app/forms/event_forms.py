# app/forms/event_forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateTimeLocalField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class EventForm(FlaskForm):
    title = StringField('Event Title', validators=[DataRequired(), Length(min=3, max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    location = StringField('Location', validators=[Optional(), Length(max=100)])
    event_type = SelectField('Event Type', validators=[DataRequired()], choices=[
        ('league_game', 'League Game'),
        ('tournament', 'Tournament'),
        ('friendly_match', 'Friendly Match'),
        ('custom', 'Custom Event')
    ])
    start_datetime = DateTimeLocalField('Start Date & Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    end_datetime = DateTimeLocalField('End Date & Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    season = SelectField('Season', validators=[Optional()], choices=[])  # Adding the season field
    submit = SubmitField('Save Event')