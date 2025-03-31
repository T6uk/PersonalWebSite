# app/events/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateTimeLocalField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from datetime import datetime


class EventTypeForm(FlaskForm):
    name = StringField('Event Type Name', validators=[DataRequired(), Length(max=64)])
    description = TextAreaField('Description')
    submit = SubmitField('Save')


class EventForm(FlaskForm):
    title = StringField('Event Title', validators=[DataRequired(), Length(max=120)])
    event_type = SelectField('Event Type', coerce=int, validators=[DataRequired()])
    parent_event = SelectField('Tournament', coerce=int, validators=[Optional()], default=0)
    opponent = StringField('Opponent', validators=[Length(max=120)])
    location = StringField('Location', validators=[Length(max=120)])
    event_date = DateTimeLocalField('Event Date', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    description = TextAreaField('Description')
    result = StringField('Result', validators=[Length(max=20)])
    team_score = IntegerField('Our Score', validators=[NumberRange(min=0), Optional()], default=0)
    opponent_score = IntegerField('Opponent Score', validators=[NumberRange(min=0), Optional()], default=0)
    submit = SubmitField('Save')

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        from app.models.event import EventType, Event

        # Set event type choices
        self.event_type.choices = [(e.id, e.name) for e in EventType.query.order_by('name')]

        # Set tournament choices (only events with tournament type)
        tournament_type = EventType.query.filter_by(name='Tournament').first()
        tournament_choices = [(0, 'None')]

        if tournament_type:
            tournaments = Event.query.filter_by(event_type_id=tournament_type.id).order_by(
                Event.event_date.desc()).all()
            tournament_choices += [(t.id, t.title) for t in tournaments]

        self.parent_event.choices = tournament_choices


class GamePlayerStatForm(FlaskForm):
    player = SelectField('Player', coerce=int, validators=[DataRequired()])
    minutes_played = IntegerField('Minutes Played', validators=[NumberRange(min=0, max=120)], default=0)
    goals = IntegerField('Goals', validators=[NumberRange(min=0)], default=0)
    assists = IntegerField('Assists', validators=[NumberRange(min=0)], default=0)
    yellow_cards = IntegerField('Yellow Cards', validators=[NumberRange(min=0, max=2)], default=0)
    red_cards = IntegerField('Red Cards', validators=[NumberRange(min=0, max=1)], default=0)
    shots = IntegerField('Shots', validators=[NumberRange(min=0)], default=0)
    shots_on_target = IntegerField('Shots on Target', validators=[NumberRange(min=0)], default=0)
    passes = IntegerField('Passes', validators=[NumberRange(min=0)], default=0)
    pass_accuracy = IntegerField('Pass Accuracy %', validators=[NumberRange(min=0, max=100)], default=0)
    tackles = IntegerField('Tackles', validators=[NumberRange(min=0)], default=0)
    fouls_committed = IntegerField('Fouls Committed', validators=[NumberRange(min=0)], default=0)
    fouls_suffered = IntegerField('Fouls Suffered', validators=[NumberRange(min=0)], default=0)
    submit = SubmitField('Save')

    def __init__(self, *args, **kwargs):
        super(GamePlayerStatForm, self).__init__(*args, **kwargs)
        from app.models.user import User
        self.player.choices = [(u.id, f"{u.first_name} {u.last_name}")
                               for u in User.query.filter_by(user_type='player').order_by('last_name')]