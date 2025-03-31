from app import create_app, create_admin_user
from app.extensions import db

app = create_app()

with app.app_context():
    db.create_all()
    create_admin_user()

if __name__ == '__main__':
    app.run(debug=True)
