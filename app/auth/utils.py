from app import db
from app.models import User, Role

def create_initial_admin():
    """Create initial admin account if it doesn't exist"""
    admin = User.query.filter_by(role=Role.ADMIN).first()
    if admin is None:
        admin = User(
            username='admin',
            email='admin@fcmara.com',
            role=Role.ADMIN
        )
        admin.set_password('admin123')  # Default password - should be changed immediately
        db.session.add(admin)
        db.session.commit()
        print('Initial admin account created.')
    else:
        print('Admin account already exists.')