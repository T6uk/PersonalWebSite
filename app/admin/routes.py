from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.admin import bp
from app.admin.forms import CreateUserForm
from app.models import User
from functools import wraps


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('You do not have permission to access this page', 'danger')
            return redirect(url_for('core.home'))
        return f(*args, **kwargs)

    return decorated_function


@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    return render_template('admin/dashboard.html', title='Admin Dashboard')


@bp.route('/create-user', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    form = CreateUserForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'User account created for {form.username.data}!', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/create_user.html', title='Create User', form=form)


@bp.route('/users')
@login_required
@admin_required
def view_users():
    users = User.query.all()
    return render_template('admin/view_users.html', title='All Users', users=users)