from flask import current_app, url_for
from flask_mail import Message
from app.extensions import mail
from itsdangerous import URLSafeTimedSerializer

def send_reset_email(user):
    token = generate_reset_token(user.email)
    msg = Message('Password Reset Request',
                 sender=current_app.config['MAIL_USERNAME'],
                 recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('auth.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='password-reset-salt')

def verify_reset_token(token, expires_sec=1800):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=expires_sec)
    except:
        return None
    return User.query.filter_by(email=email).first()