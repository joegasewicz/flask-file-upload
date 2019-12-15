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

        # Setup

        db = SQLAlchemy()
        file_uploads = FileUploads()

        # FlaskFileUploads needs to do some work with your SqlAlchemy model
        # Pass in an instance after Flask-SqlAlchemy's `db instance
        class MyModel(db, uploads):
           my_video = file_uploads.Column()
           placeholder_img = file_uploads.Column()

        # define files to be upload:
        # (This is an example of a video with placeholder image attached):

        my_video = request.files["my_video"]
        placeholder_img = request.files["placeholder_img"]


        # Get main form data and pass to your SqlAlchemy Model
        blog_post = BlogPostModel(title="Hello World Today")

        file_uploads.save_files(blog_post, files={
            "my_video": my_video,
            "placeholder_img": placeholder_img,
        })

        # Update files
        file_uploads.update_files(BlogPostModel, files=[my_video])

        # Update file name
        file_uploads.update_file_name(BlogPostModel, my_video, new_filename="new_name")

        # Stream a file
        # First get your entity
        my_blog_post = BlogModel().get(id=1)  # Or your way of getting an entity
        file_upload.stream_file(blog_post, filename=["my_video"])

        # File Url paths
        file_upload.get_file_url(blog_post, filename="placeholder_img")



"""
import os
from warnings import warn
from flask import send_from_directory, Flask
from werkzeug.utils import secure_filename
from typing import Any, List, Tuple, Dict

from ._config import Config


class FileUploads:

    app: Flask

    config: Config = Config()

    model: Tuple = None

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.config.init_config(app)

    def allowed_file(self, filename):
        return "." in filename and \
            filename.rsplit(".", 1)[1].lower() in self.config.allowed_extensions

    def save_files(self, model: Tuple, **kwargs) -> List[Dict[str, Any]]:
        """
        :param model: Sets the model attribute
        :param kwargs: files: List - request.files
        :return:
        """
        self.model = model
        file_data = []
        for f in kwargs.get("files"):
            file_data.append(self.create_file_dict(f))
        return file_data

    def create_file_dict(self, file):
        if file.filename != "" and file and self.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            mime_type = file.content_type
            file_type = filename.split(".")[1]
            return {
                f"_filename": filename,
                f"_mime_type": mime_type,
                f"_file_type": file_type,
            }
        else:
            warn("Flask-File-Upload: No files were saved")
            return {}

    def filename_index(self, attr):
        """Gets the filename index"""
        class_attrs = dir(self.model)
        for a in class_attrs:
            if attr == a:
                return f"{self.int_from_str(attr)}"
        return attr

    def int_from_str(self, name: str):
        """
        Check to see if a number exists at the
        end of a string & add 1
        :param name:
        :return:
        """
        nums = []
        name_str = []
        for s in name:
            try:
                nums.append(int(s))
            except ValueError:
                name_str.append(s)
        if len(nums) > 0:
            return f'{"".join(name_str)}{(int("".join(map(str, nums)))+1)}'
        else:
            return f'{name}_1'

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

    def stream_file(self, model, **kwargs):
        """TODO """
        return send_from_directory(
            self.config["UPLOAD_FOLDER"],
            f"{model.id}"
            f"{self.get_file_ext(kwargs.get('filename'))}"
            f".{model['file_type']}",
            conditional=True,
        )

    def get_file_ext(self, filename):
        """
        This checks which file in the table we need to stream
        and returns the extension name
        :param filename:
        :return:
        """
        pass

    def get_file_url(self, model, **kwargs):
        """returns file url"""
        pass