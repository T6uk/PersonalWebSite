from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SelectField, DateField, TextAreaField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, NumberRange

class LeagueForm(FlaskForm):
    name = StringField('League Name', validators=[DataRequired(), Length(max=128)])
    season_id = SelectField('Season', coerce=int, validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[Optional()])
    location = StringField('Location', validators=[Optional(), Length(max=128)])
    description = TextAreaField('Description', validators=[Optional()])
    image = FileField('League Image', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    format = SelectField('Format', choices=[
        ('round-robin', 'Round Robin'),
        ('home-away', 'Home and Away'),
    ], validators=[DataRequired()])
    num_teams = IntegerField('Number of Teams', validators=[Optional(), NumberRange(min=2)])
    points_for_win = IntegerField('Points for Win', validators=[Optional(), NumberRange(min=1)], default=3)
    points_for_draw = IntegerField('Points for Draw', validators=[Optional(), NumberRange(min=0)], default=1)
    submit = SubmitField('Save League')