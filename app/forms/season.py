from flask_wtf import FlaskForm
from wtforms import StringField, DateField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional, Length

class SeasonForm(FlaskForm):
    name = StringField('Season Name', validators=[DataRequired(), Length(max=32)])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[Optional()])
    is_current = BooleanField('Current Season', default=False)
    submit = SubmitField('Save Season')