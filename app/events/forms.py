from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateTimeLocalField, SubmitField
from wtforms.validators import DataRequired, Length
from datetime import datetime

class EventTypeForm(FlaskForm):
    name = StringField('Event Type Name', validators=[DataRequired(), Length(max=64)])
    description = TextAreaField('Description')
    submit = SubmitField('Save')


class EventForm(FlaskForm):
    title = StringField('Event Title', validators=[DataRequired(), Length(max=120)])
    event_type = SelectField('Event Type', coerce=int, validators=[DataRequired()])
    opponent = StringField('Opponent', validators=[Length(max=120)])
    location = StringField('Location', validators=[Length(max=120)])
    event_date = DateTimeLocalField('Event Date', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    description = TextAreaField('Description')
    result = StringField('Result', validators=[Length(max=20)])
    score = StringField('Score', validators=[Length(max=20)])
    submit = SubmitField('Save')

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        from app.models.event import EventType
        self.event_type.choices = [(e.id, e.name) for e in EventType.query.order_by('name')]