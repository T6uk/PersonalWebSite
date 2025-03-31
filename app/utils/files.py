import os
import secrets
from PIL import Image
from flask import current_app


def save_picture(form_picture, folder='profiles', size=(150, 150)):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext

    # Determine target folder
    if folder == 'profiles':
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'profiles')
    elif folder == 'trophies':
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'trophies')
    else:
        upload_folder = current_app.config['UPLOAD_FOLDER']

    # Ensure folder exists
    os.makedirs(upload_folder, exist_ok=True)

    picture_path = os.path.join(upload_folder, picture_fn)

    # Resize image
    i = Image.open(form_picture)
    i.thumbnail(size)
    i.save(picture_path)

    return picture_fn
