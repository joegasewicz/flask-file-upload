"""
    Flask File Upload

    Library that works with Flask & SqlAlchemy to store
    files in your database

    orig_name
    mime_type
    file_type

"""
import os
from warnings import warn
from werkzeug.utils import secure_filename


from app import ALLOWED_EXTENSIONS


def allowed_file(filename):
    return "." in filename and \
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def create_upload(file):
    if file.filename != "" and file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        mime_type = file.content_type
        file_type = filename.split(".")[1]
        return {
            f"filename": filename,
            f"mime_type": mime_type,
            f"file_type": file_type,
        }
    else:
        warn("Flask-File-Upload: No files were saved")
        return {}


def update_model_attr():
    """
    Updates the model with attributes:
        - orig_name
        - mime_type
        - file_type
    :return:
    """


def save_file(file, config):
    file.save(os.path.join(config["UPLOAD_FOLDER"]))
