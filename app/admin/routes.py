from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.admin.forms import UserCreateForm, UserUpdateForm
from app.models.user import User
from app.extensions import db, bcrypt
from app.utils.decorators import admin_required
from app.utils.files import save_picture
import os

admin = Blueprint('admin', __name__)


@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    users_count = User.query.count()
    players_count = User.query.filter_by(user_type='player').count()
    admins_count = User.query.filter_by(user_type='admin').count()
    return render_template('admin/dashboard.html',
                           title='Admin Dashboard',
                           users_count=users_count,
                           players_count=players_count,
                           admins_count=admins_count)


@admin.route('/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.date_joined.desc()).paginate(page=page, per_page=10)
    return render_template('admin/users.html', title='User Management', users=users)


@admin.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    form = UserCreateForm()
    if form.validate_on_submit():
        if form.profile_picture.data:
            picture_file = save_picture(form.profile_picture.data)
        else:
            picture_file = 'default.jpg'

        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            user_type=form.user_type.data,
            profile_picture=picture_file
        )
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('admin.users'))

    return render_template('admin/create_user.html', title='Create User', form=form)


@admin.route('/users/<int:user_id>/update', methods=['GET', 'POST'])
@login_required
@admin_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserUpdateForm(user.username, user.email)

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.user_type = form.user_type.data

        if form.profile_picture.data:
            if user.profile_picture != 'default.jpg':
                # Delete old profile picture
                old_picture_path = os.path.join(current_app.root_path, 'static/uploads', user.profile_picture)
                if os.path.exists(old_picture_path):
                    os.remove(old_picture_path)

            picture_file = save_picture(form.profile_picture.data)
            user.profile_picture = picture_file

        db.session.commit()
        flash('User has been updated!', 'success')
        return redirect(url_for('admin.users'))
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.user_type.data = user.user_type

    return render_template('admin/update_user.html', title='Update User', form=form, user=user)


@admin.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    if user == current_user:
        flash('You cannot delete your own account!', 'danger')
        return redirect(url_for('admin.users'))

    # Delete profile picture if not default
    if user.profile_picture != 'default.jpg':
        picture_path = os.path.join(current_app.root_path, 'static/uploads', user.profile_picture)
        if os.path.exists(picture_path):
            os.remove(picture_path)

    db.session.delete(user)
    db.session.commit()

    flash('User has been deleted!', 'success')
    return redirect(url_for('admin.users'))