from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SelectField, DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, Length

class FriendlyForm(FlaskForm):
    name = StringField('Friendly Name', validators=[DataRequired(), Length(max=128)])
    season_id = SelectField('Season', coerce=int, validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[Optional()])
    location = StringField('Location', validators=[Optional(), Length(max=128)])
    description = TextAreaField('Description', validators=[Optional()])
    image = FileField('Event Image', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    purpose = StringField('Purpose', validators=[Optional(), Length(max=128)])
    submit = SubmitField('Save Friendly')