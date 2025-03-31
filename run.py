from app import create_app, create_admin_user, init_event_types
from app.extensions import db

app = create_app()

with app.app_context():
    db.create_all()
    create_admin_user()
    init_event_types()

if __name__ == '__main__':
    app.run(debug=True)
