from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SelectField, DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, Length

class EventForm(FlaskForm):
    name = StringField('Event Name', validators=[DataRequired(), Length(max=128)])
    event_type = SelectField('Event Type',
                           choices=[('league', 'League Game'),
                                   ('tournament', 'Tournament'),
                                   ('friendly', 'Friendly')],
                           validators=[DataRequired()])
    season = StringField('Season', validators=[DataRequired(), Length(max=32)])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[Optional()])
    location = StringField('Location', validators=[Optional(), Length(max=128)])
    description = TextAreaField('Description', validators=[Optional()])
    image = FileField('Event Image', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    submit = SubmitField('Save Event')