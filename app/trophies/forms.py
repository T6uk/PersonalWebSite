from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class TrophyForm(FlaskForm):
    name = StringField('Trophy Name', validators=[DataRequired()])
    year = IntegerField('Year', validators=[DataRequired(), NumberRange(min=1800, max=2100)])
    competition = StringField('Competition', validators=[DataRequired()])
    description = TextAreaField('Description')
    image = FileField('Trophy Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Save')
