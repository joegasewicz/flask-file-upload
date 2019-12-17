"""
Flask File Upload

    # Public api:

        file_uploads = FileUpload(app)

    ##### General Flask config options
    ````python
        UPLOAD_FOLDER = join(dirname(realpath(__file__)), "uploads/lessons")
        ALLOWED_EXTENSIONS = ["jpg", "png", "mov", "mp4", "mpg"]
        MAX_CONTENT_LENGTH = 1000 * 1024 * 1024  # 1000mb
    ````


    ##### Setup
    ````python
        db = SQLAlchemy()
        file_uploads = FileUpload()
    ````


    ##### FlaskFileUploads needs to do some work with your SqlAlchemy model
    Decorate your SqlAlchemy model with your files
     ````python
        @file_uploads.Model("my_video")
        @file_uploads.Model("placeholder_img")
        class MyModel(db, uploads):
           id = Model(Integer, primary_key=True)
    ````

    ##### define files to be upload:
        (This is an example of a video with placeholder image attached):
    ````python
        my_video = request.files["my_video"]
        placeholder_img = request.files["placeholder_img"]
    ````


    ##### Get main form data and pass to your SqlAlchemy Model
    ````python
        blog_post = BlogPostModel(title="Hello World Today")

        file_uploads.save_files(blog_post, files={
            "my_video": my_video,
            "placeholder_img": placeholder_img,
        })
    ````

    ##### Update files
    ````python
        file_uploads.update_files(BlogPostModel, files=[my_video])
    ````


    ##### Update file name
    ````python
        file_uploads.update_file_name(BlogPostModel, my_video, new_filename="new_name")
    ````


    ##### Stream a file
    ````python
        First get your entity
        my_blog_post = BlogModel().get(id=1)  # Or your way of getting an entity
        file_upload.stream_file(blog_post, filename="my_video")
    ````


    ##### File Url paths
    ````python
        file_upload.get_file_url(blog_post, filename="placeholder_img")
    ````


"""
import os
from warnings import warn
from flask import send_from_directory, Flask
from werkzeug.utils import secure_filename
from typing import Any, List, Tuple, Dict

from ._config import Config
from .model import Model
from .column import Column
from .file_utils import FileUtils


class FileUpload:

    app: Flask

    config: Config = Config()

    file_data: List[Any]

    file_utils: FileUtils

    def __init__(self, app=None):
        self.Model = Model
        self.Column = Column
        if app:
            self.init_app(app)

    def check_attrs(self, model: Any, attr: str):
        """
        Before we can set the attribute on the Model we check
        that this attributes exists so it matches with the
        db's table columns.
        :param model:
        :param attr:
        :return:
        """
        if not hasattr(model, attr):
            raise AttributeError(
                "Flask-File-Upload: Attribute does not exist on your model, "
                "please check your files has been declared correctly on your model. "
                "See https://github.com/joegasewicz/Flask-File-Upload"
            )

    def create_file_dict(self, filename: str, file):
        """
        :param file:
        :return:
        """
        if file.filename != "" and file and self.file_utils.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            mime_type = file.content_type
            file_type = filename.split(".")[1]
            return {
                f"{filename}__{self.Model.keys[0]}": filename,
                f"{filename}__{self.Model.keys[1]}": mime_type,
                f"{filename}__{self.Model.keys[2]}": file_type,
            }
        else:
            warn("Flask-File-Upload: No files were saved")
            return {}

    def get_store_name(self, model):
        """TODO Attach to model"""
        model.store_name = f"{model.id}.{model.file_type}"

    def init_app(self, app):
        self.app = app
        self.config.init_config(app)

    def save_files(self, model, **kwargs) -> None:
        """
        Save in dir based on __tablename__ / id / filename.mp4
        """
        self.file_utils = FileUtils(
            model,
            self.config,
            id=self.Model.get_primary_key(model),
            table_name=self.Model.get_table_name(model)
        )
        self.set_file_data(**kwargs)
        self.set_model_attrs(model)

    def set_file_data(self, **file_data):
        for k, v in file_data.get("files").items():
            self.file_data.append(self.create_file_dict(k, v))
        return self.file_data

    def set_model_attrs(self, model: Any) -> None:
        """
        :param model:
        :return: None
        """
        for d in self.file_data:
            for k, v in d.items():
                self.check_attrs(model, k)
                setattr(model, k, v)

    def update_model_attr(self):
        """
        Updates the model with attributes:
            - orig_name
            - mime_type
            - file_type
        :return:
        """
        pass

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