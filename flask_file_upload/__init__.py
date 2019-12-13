"""
    Flask File Upload

    Library that works with Flask & SqlAlchemy to store
    files in your database

    orig_name
    mime_type
    file_type

    # Public api:

        file_uploads = FileUploads(app)

        # General Flask config options
        UPLOAD_FOLDER = join(dirname(realpath(__file__)), "uploads/lessons")
        ALLOWED_EXTENSIONS = ["jpg", "png", "mov", "mp4", "mpg"]
        MAX_CONTENT_LENGTH = 1000 * 1024 * 1024  # 1000mb

        # define files to be upload:
        # (This is an example of a video with placeholder image attached):

        my_video = request.files["my_video"]
        placeholder_img = request.files["placeholder_img"]

        # Get main form data and pass to yoour SqlAlchemy Model
        blog_post = blogPostModel(title="Hello World Today")

        file_uploads.create_uploads(blog_post, files=[my_video, placeholder_img])

"""
import os
from warnings import warn
from werkzeug.utils import secure_filename


from app import ALLOWED_EXTENSIONS


class FileUploads:

    def allowed_file(self, filename):
        return "." in filename and \
            filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

    def create_uploads(self, **kwargs):
        file_data = []
        for f in kwargs.get("files"):
            file_data.append(self.create_file_dict(f))

    def create_file_dict(self, file):
        if file.filename != "" and file and self.allowed_file(file.filename):
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

    def update_model_attr(self):
        """
        Updates the model with attributes:
            - orig_name
            - mime_type
            - file_type
        :return:
        """
        pass

    def get_store_name(self, model):
        """TODO Attach to model"""
        model.store_name = f"{model.id}.{model.file_type}"

    def save_file(self, file, config):
        file.save(os.path.join(config["UPLOAD_FOLDER"]))
