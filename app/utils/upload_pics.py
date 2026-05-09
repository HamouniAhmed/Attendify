from werkzeug.utils import secure_filename
import os
from flask import current_app

# Re-use or import the save_picture function if it's moved to a utils module
def save_picture(form_picture):
    """Saves uploaded picture and returns the filename."""
    if not form_picture:
        return None

    filename = secure_filename(form_picture.filename)
    upload_folder = os.path.join(current_app.root_path, 'static/uploads')
    picture_path = os.path.join(upload_folder, filename)
    os.makedirs(upload_folder, exist_ok=True)
    form_picture.save(picture_path)
    return os.path.join('uploads', filename).replace("\\", "/")