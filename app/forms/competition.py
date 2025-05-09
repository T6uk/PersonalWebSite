from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SelectField, DateField, TextAreaField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, NumberRange

# Base Competition Form
class CompetitionForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=128)])
    season_id = SelectField('Season', coerce=int, validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[Optional()])
    location = StringField('Location', validators=[Optional(), Length(max=128)])
    description = TextAreaField('Description', validators=[Optional()])
    image = FileField('Image', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])

# League Form
class LeagueForm(CompetitionForm):
    format = SelectField('Format', choices=[
        ('round-robin', 'Round Robin'),
        ('home-away', 'Home and Away'),
    ], validators=[DataRequired()])
    num_teams = IntegerField('Number of Teams', validators=[Optional(), NumberRange(min=2)])
    points_for_win = IntegerField('Points for Win', validators=[Optional(), NumberRange(min=1)], default=3)
    points_for_draw = IntegerField('Points for Draw', validators=[Optional(), NumberRange(min=0)], default=1)
    submit = SubmitField('Save League')

# Tournament Form
class TournamentForm(CompetitionForm):
    format = SelectField('Format', choices=[
        ('knockout', 'Knockout'),
        ('group+knockout', 'Group Stage + Knockout'),
        ('league', 'League Format'),
    ], validators=[DataRequired()])
    num_teams = IntegerField('Number of Teams', validators=[Optional(), NumberRange(min=2)])
    current_round = StringField('Current Round', validators=[Optional(), Length(max=64)])
    submit = SubmitField('Save Tournament')

# Friendly Form
class FriendlyForm(CompetitionForm):
    purpose = StringField('Purpose', validators=[Optional(), Length(max=128)])
    submit = SubmitField('Save Friendly')