from flask import render_template
from app.core import bp

@bp.route('/')
@bp.route('/home')
def home():
    return render_template('core/home.html', title='Home')

@bp.route('/about')
def about():
    return render_template('core/about.html', title='About')