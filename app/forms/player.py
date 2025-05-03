from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, IntegerField, TextAreaField, DateField, FloatField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange, Length

class PlayerForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=64)])
    position = StringField('Position', validators=[DataRequired(), Length(max=64)])
    jersey_number = IntegerField('Jersey Number', validators=[Optional(), NumberRange(min=1, max=99)])
    date_of_birth = DateField('Date of Birth', validators=[Optional()])
    height = FloatField('Height (cm)', validators=[Optional(), NumberRange(min=120, max=250)])
    weight = FloatField('Weight (kg)', validators=[Optional(), NumberRange(min=40, max=150)])
    nationality = StringField('Nationality', validators=[Optional(), Length(max=64)])
    bio = TextAreaField('Biography', validators=[Optional()])
    image = FileField('Profile Image', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    is_active = BooleanField('Active Player', default=True)
    submit = SubmitField('Save Player')