from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash
import os

app = create_app()


# Create an initialization function
def init_db():
    # Create database tables if they don't exist
    db.create_all()

    # Check if admin user exists
    admin = User.query.filter_by(username='mara').first()
    if not admin:
        # Create admin user with password from environment or default
        admin_password = os.environ.get('ADMIN_PASSWORD', '1234')
        hashed_password = generate_password_hash(admin_password)
        admin = User(username='mara', password_hash=hashed_password, is_admin=True)
        db.session.add(admin)
        db.session.commit()
        print("Admin user created")


# Initialize the database when the app is run
with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(debug=True)