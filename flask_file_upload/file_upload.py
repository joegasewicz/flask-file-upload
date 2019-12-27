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
        @file_uploads.Model("my_placeholder")
        class MyModel(db, uploads):
           id = Model(Integer, primary_key=True)
    ````

    ##### define files to be upload:
        (This is an example of a video with placeholder image attached):
    ````python
        my_video = request.files["my_video"]
        my_placeholder = request.files["my_placeholder"]
    ````


    ##### Get main form data and pass to your SqlAlchemy Model
    ````python
        blog_post = BlogPostModel(title="Hello World Today")

        file_uploads.save_files(blog_post, files={
            "my_video": my_video,
            "my_placeholder": my_placeholder,
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
        file_upload.get_file_url(blog_post, filename="my_placeholder")
    ````


"""
import os
from warnings import warn
from flask import send_from_directory, Flask, request
from werkzeug.utils import secure_filename
from typing import Any, List, Tuple, Dict

from ._config import Config
from .model import Model
from .column import Column
from .file_utils import FileUtils
from ._model_utils import _ModelUtils


class FileUpload:

    app: Flask = None

    config: Config = Config()

    file_data: List[Dict[str, str]] = []

    files: Any = []

    file_utils: FileUtils = None

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
                f"Flask-File-Upload: Attribute {attr} does not exist on your model, "
                "please check your files has been declared correctly on your model. "
                "See https://github.com/joegasewicz/Flask-File-Upload"
            )

    def create_file_dict(self, file, attr_name: str):
        """

        :param file:
        :param attr_name:
        :return:
        """
        if file.filename != "" and file and FileUtils.allowed_file(file.filename, self.config):
            filename = secure_filename(file.filename)
            filename_key = attr_name
            mime_type = file.content_type
            file_type = file.filename.split(".")[1]
            return {
                f"{filename_key}__{_ModelUtils.keys[0]}": filename,
                f"{filename_key}__{_ModelUtils.keys[1]}": mime_type,
                f"{filename_key}__{_ModelUtils.keys[2]}": file_type,
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

    def _save_files_to_dir(self, model: Any) -> None:
        """
        :param model:
        :return None:
        """
        for f in self.files:
            id_val = _ModelUtils.get_id_value(model)
            self.file_utils.save_file(f, id_val)

    def _set_file_data(self, **file_data) -> List[Dict[str, str]]:
        """
        Adds items to files & file_data
        :key files: Dict[str: Any] Key is the filename & Value
        is the file.
        :return List[Dict[str, str]]:
        """
        for k, v in file_data.get("files").items():
            self.files.append(v)
            self.file_data.append(self.create_file_dict(v, k))
        return self.file_data

    def _set_model_attrs(self, model: Any) -> None:
        """
        :param model:
        :return: None
        """
        for d in self.file_data:
            for k, v in d.items():
                self.check_attrs(model, k)
                setattr(model, k, v)

    def stream_file(self, model, **kwargs) -> Any:
        """
        Streams a file from the directory defined by
        the Flask's UPLOAD_FOLDER your Flask app's
        configuration settings.
        :param model:
        :param kwargs:
        :return Any:
        """
        try:
            filename = kwargs['filename']
        except KeyError:
            warn("'files' is a Required Argument")
            return None

        file_type = _ModelUtils.get_by_postfix(model, filename, _ModelUtils.keys[1])

        self.file_utils = FileUtils(model, self.config)

        return send_from_directory(
            self.file_utils.get_stream_path(model.id),
            f"{filename}.{file_type}",
            conditional=True,
        )

    def save_files(self, model, **kwargs) -> Any:
        """
        :param model:
        :param kwargs:
        :return Any:
        """
        # Warning: These methods need to set members on the Model class
        # before we instantiate FileUtils()
        self._set_file_data(**kwargs)
        self._set_model_attrs(model)

        self.file_utils = FileUtils(model, self.config)

        # Save files to dirs
        self._save_files_to_dir(model)

        return model

    def update_files(self, model: Any, db=None, **kwargs):
        """
        :param model:
        :param db: Default is None which is not Recommended. If db is None,
        then only the files on the server are removed & the model is updated with
        each attribute set to None but the session is not commited (This could cause
        your database & files on server to be out of sync if you fail to commit
        the session.
        If you encounter an exception before you can commit the session then you
        can call either `update_model_clean_up()` or `update_files_clean_up()` to
        update the model or update the files on the server respectively.
        :key files Dict[str, Any]: A dict with the key
        representing the model attr name & file as value.
        :return Any: Returns the model back
        """
        try:
            files = kwargs["files"]
        except KeyError:
            warn("'files' is a Required Argument")
            return None

        original_file_names = []

        for f in files:
            value = _ModelUtils.get_by_postfix(model, f, "file_name")
            original_file_names.append(value)

        # Set file_data
        self._set_file_data(**kwargs)
        self._set_model_attrs(model)

        self.file_utils = FileUtils(model, self.config)

        # Save files to dirs
        self._save_files_to_dir(model)

        # remove original files from directory
        for f in original_file_names:
            os.remove(f"{self.file_utils.get_stream_path(model.id)}/{f}")

        # if a db arg is provided then commit changes to db
        if db:
            db.session.add(model)
            db.session.commit()
            return None
        else:
            return model

    def get_file_url(self, model: Any, **kwargs) -> str:
        """
        :param model:
        :param kwargs:
        :return:
        """
        try:
            filename = kwargs["filename"]
            self.file_utils = FileUtils(model, self.config)
            file_path = self.file_utils.get_file_path(model.id, filename)
            file_type = _ModelUtils.get_by_postfix(model, filename, "file_type")
            return f"{request.url}{file_path}.{file_type}"
        except AttributeError:
            AttributeError("[FLASK_FILE_UPLOAD] You must declare a filename kwarg")

    def delete_files(self, model, db=None, **kwargs) -> None:
        """
        :param model:
        :param db:
        :param kwargs:
        :return None:
        """
        try:
            files: List[str] = kwargs["files"]
        except KeyError:
            warn("'files' is a Required Argument")
            return None

        self.file_utils = FileUtils(model, self.config)

        for f in files:
            file_type = _ModelUtils.get_by_postfix(model, f, 'file_type')
            file_path = f"{self.file_utils.get_stream_path(model.id)}/{f}.{file_type}"
            os.remove(f"{file_path}")

        for f_name in files:
            for postfix in _ModelUtils.keys:
                print(_ModelUtils.add_postfix(f_name, postfix))
                setattr(model, _ModelUtils.add_postfix(f_name, postfix), None)

        print(dir(model))

        if db:
            db.session.add(model)
            db.session.commit()
            return model
        else:
            return model
