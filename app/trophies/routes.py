from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required
from app.trophies.forms import TrophyForm
from app.models.trophy import Trophy
from app.extensions import db
from app.utils.decorators import admin_required
from app.utils.files import save_picture
import os

trophies = Blueprint('trophies', __name__)


@trophies.route('/')
def index():
    # Group trophies by year in descending order
    trophies_by_year = {}
    all_trophies = Trophy.query.order_by(Trophy.year.desc(), Trophy.name).all()

    for trophy in all_trophies:
        if trophy.year not in trophies_by_year:
            trophies_by_year[trophy.year] = []
        trophies_by_year[trophy.year].append(trophy)

    return render_template('trophies/index.html',
                           title='Trophy Cabinet',
                           trophies_by_year=trophies_by_year)


@trophies.route('/detail/<int:trophy_id>')
def detail(trophy_id):
    trophy = Trophy.query.get_or_404(trophy_id)
    return render_template('trophies/detail.html', title=trophy.name, trophy=trophy)


@trophies.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    form = TrophyForm()

    if form.validate_on_submit():
        if form.image.data:
            image_file = save_picture(form.image.data, folder='trophies')
        else:
            image_file = 'default_trophy.jpg'

        trophy = Trophy(
            name=form.name.data,
            year=form.year.data,
            competition=form.competition.data,
            description=form.description.data,
            image=image_file
        )

        db.session.add(trophy)
        db.session.commit()

        flash('Trophy has been added to the cabinet!', 'success')
        return redirect(url_for('trophies.index'))

    return render_template('trophies/create.html', title='Add Trophy', form=form)


@trophies.route('/update/<int:trophy_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def update(trophy_id):
    trophy = Trophy.query.get_or_404(trophy_id)
    form = TrophyForm()

    if form.validate_on_submit():
        if form.image.data:
            if trophy.image != 'default_trophy.jpg':
                # Delete old image
                old_image_path = os.path.join(current_app.root_path, 'static/uploads/trophies', trophy.image)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)

            image_file = save_picture(form.image.data, folder='trophies')
            trophy.image = image_file

        trophy.name = form.name.data
        trophy.year = form.year.data
        trophy.competition = form.competition.data
        trophy.description = form.description.data

        db.session.commit()

        flash('Trophy details have been updated!', 'success')
        return redirect(url_for('trophies.detail', trophy_id=trophy.id))
    elif request.method == 'GET':
        form.name.data = trophy.name
        form.year.data = trophy.year
        form.competition.data = trophy.competition
        form.description.data = trophy.description

    return render_template('trophies/update.html', title='Update Trophy', form=form, trophy=trophy)


@trophies.route('/delete/<int:trophy_id>', methods=['POST'])
@login_required
@admin_required
def delete(trophy_id):
    trophy = Trophy.query.get_or_404(trophy_id)

    if trophy.image != 'default_trophy.jpg':
        # Delete image file
        image_path = os.path.join(current_app.root_path, 'static/uploads/trophies', trophy.image)
        if os.path.exists(image_path):
            os.remove(image_path)

    db.session.delete(trophy)
    db.session.commit()

    flash('Trophy has been removed from the cabinet!', 'success')
    return redirect(url_for('trophies.index'))