from datetime import datetime


def register_filters(app):
    """Register custom Jinja2 filters with the Flask app"""

    @app.template_filter('date_format')
    def date_format(value, format='%d %b %Y'):
        """Format a date according to the given format."""
        if isinstance(value, str):
            try:
                value = datetime.strptime(value, '%Y-%m-%d')
            except ValueError:
                return value
        return value.strftime(format)

    @app.template_filter('time_format')
    def time_format(value, format='%H:%M'):
        """Format a time according to the given format."""
        if isinstance(value, str):
            try:
                value = datetime.strptime(value, '%H:%M:%S')
            except ValueError:
                return value
        return value.strftime(format)

    @app.template_filter('datetime_format')
    def datetime_format(value, format='%d %b %Y %H:%M'):
        """Format a datetime according to the given format."""
        if isinstance(value, str):
            try:
                value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return value
        return value.strftime(format)

    @app.template_filter('timesince')
    def timesince(value):
        """Returns a string representing time since the given datetime."""
        now = datetime.now()
        if isinstance(value, str):
            try:
                value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return value

        diff = now - value

        if diff.days > 365:
            years = diff.days // 365
            return f"{years} year{'s' if years != 1 else ''} ago"
        elif diff.days > 30:
            months = diff.days // 30
            return f"{months} month{'s' if months != 1 else ''} ago"
        elif diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "just now"

    @app.template_filter('truncate_words')
    def truncate_words(s, num=30, end='...'):
        """Truncate a string after a certain number of words."""
        words = s.split()
        if len(words) > num:
            return ' '.join(words[:num]) + end
        return s

    @app.template_filter('now')
    def now(format_string='%Y'):
        """Return the current time formatted according to the format string."""
        return datetime.now().strftime(format_string)

    @app.template_filter('age')
    def age(dob):
        """Calculate age based on date of birth."""
        if not dob:
            return None
        today = datetime.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    @app.template_filter('slice')
    def slice_filter(iterable, start, end=None, step=1):
        """Slice an iterable."""
        if end is None:
            return iterable[start::step]
        return iterable[start:end:step]