# app/forms/tournament.py
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SelectField, DateField, TextAreaField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, NumberRange

class TournamentForm(FlaskForm):
    name = StringField('Tournament Name', validators=[DataRequired(), Length(max=128)])
    season_id = SelectField('Season', coerce=int, validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[Optional()])
    location = StringField('Location', validators=[Optional(), Length(max=128)])
    description = TextAreaField('Description', validators=[Optional()])
    image = FileField('Tournament Image', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    format = SelectField('Format', choices=[
        ('knockout', 'Knockout'),
        ('group+knockout', 'Group Stage + Knockout'),
        ('league', 'League Format'),
    ], validators=[DataRequired()])
    num_teams = IntegerField('Number of Teams', validators=[Optional(), NumberRange(min=2)])
    submit = SubmitField('Save Tournament')