def init_app(app):
    """Initialize filters for the app."""

    @app.template_filter('ordinal')
    def ordinal_filter(value):
        """Format a number as an ordinal."""
        try:
            value = int(value)
        except (TypeError, ValueError):
            return value

        if value % 100 in (11, 12, 13):
            return f"{value}th"

        return {
            1: f"{value}st",
            2: f"{value}nd",
            3: f"{value}rd"
        }.get(value % 10, f"{value}th")