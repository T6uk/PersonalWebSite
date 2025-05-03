from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length, Optional

class TrophyForm(FlaskForm):
    name = StringField('Trophy Name', validators=[DataRequired(), Length(max=128)])
    competition = StringField('Competition', validators=[DataRequired(), Length(max=128)])
    year = IntegerField('Year', validators=[DataRequired(), NumberRange(min=1900, max=2100)])
    description = TextAreaField('Description', validators=[Optional()])
    image = FileField('Trophy Image', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    submit = SubmitField('Save Trophy')