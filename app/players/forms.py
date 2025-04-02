from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, TextAreaField, DateField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange, Length

class PlayerProfileForm(FlaskForm):
    position = SelectField('Position', choices=[
        ('goalkeeper', 'Goalkeeper'),
        ('defender', 'Defender'),
        ('midfielder', 'Midfielder'),
        ('forward', 'Forward')
    ], validators=[DataRequired()])
    jersey_number = IntegerField('Jersey Number', validators=[NumberRange(min=1, max=99)])
    height = IntegerField('Height (cm)', validators=[Optional(), NumberRange(min=100, max=250)])
    weight = IntegerField('Weight (kg)', validators=[Optional(), NumberRange(min=30, max=150)])
    date_of_birth = DateField('Date of Birth', format='%Y-%m-%d', validators=[Optional()])
    dominant_foot = SelectField('Dominant Foot', choices=[
        ('right', 'Right'),
        ('left', 'Left'),
        ('both', 'Both')
    ], validators=[Optional()])
    bio = TextAreaField('Bio', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Update Profile')