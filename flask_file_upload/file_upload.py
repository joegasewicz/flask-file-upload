"""
FileUpload Class
================
"""
import os
from warnings import warn
from flask import send_from_directory, Flask, request
from werkzeug.utils import secure_filename
from typing import Any, List, Dict, Union

from ._config import Config
from .model import Model
from .column import Column
from .file_utils import FileUtils
from ._model_utils import _ModelUtils


class FileUpload:
    """
    :param app: Flask application instance
    """

    #: The Flask application instance: ``app = Flask(__name__)``.
    #: We can either pass the instance to ``FileUpload(app)`` or
    #: to the ``init_app(app)`` method::
    #:
    #:    app = Flask(__name__)
    #:
    #:    db = SQLAlchemy()
    #:    file_upload = FileUpload()
    #:
    #:    # An example using the Flask factory pattern
    #:    def create_app():
    #:        db.init_app(app)
    #:        file_upload.init_app(app)
    #:
    #:    # Or we can pass the Flask app instance directly:
    #:    db = SQLAlchemy(app)
    #:    file_upload = FileUpload(app)
    #:    app: Flask = None
    app: Flask = None

    #: The configuration class used for this library.
    #: See :class:`~flask_file_upload._config` for more information.
    config: Config = Config()

    #: All the file related model attributes & values are stored
    #: here as a list of dicts.
    file_data: List[Dict[str, str]] = []

    #: A record of the original filenames used when saving files
    #: to the server.
    files: Any = []

    #: A class containing utility methods for working with files.
    #: See :class:`flask_file_upload.file_utils` for more information.
    file_utils: FileUtils = None

    def __init__(self, app=None):
        """
        The Flask application instance: ``app = Flask(__name__)``.
        :param app: Flask application instance
        """
        self.Model = Model
        self.Column = Column
        if app:
            self.init_app(app)

    def delete_files(self, model: Any, db=None, **kwargs) -> Union[Any, None]:
        """
        Public method for removing stored files from the server & database.
        This method will remove all files passed to the kwarg ``files`` list.
        It will also update the passed in SqlAlchemy ``model`` object & return
        the updated model object if ``db`` is None.

        If the ``db`` arg is passed in then the session is updated & session commited &
        this method return value is void::

            # Example using a SqlAlchemy model with an appended
            # method that fetches a single `blog`
            blogModel = BlogModel()
            blog_results = blogModel.get_one()

            # We pass the blog
            blog = file_upload.delete_files(blog_result, files=["my_video"])

            # As the `db` arg has not been passed to this method,
            # the changes would need persisting to the database:
            db.session.add(blog)
            db.session.commit()

            # If `db` is passed to this method then the updates are persisted.
            # to the session. And therefore the session has been commited &
            # no blog is returned.
            file_upload.delete_files(blog_result, db, files=["my_video"])


        :param model: Instance of a SqlAlchemy Model
        :param db: Either an instance of Flask-SqlAlchemy ``SqlAlchmey`` class or
               SqlAlchmey's ``Session`` object.
        :key files: A list of the file names decalred on your model.
        :return: SqlAlchemy model object
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
                setattr(model, _ModelUtils.add_postfix(f_name, postfix), None)
        if db:
            db.session.add(model)
            db.session.commit()
        else:
            return model

    def _check_attrs(self, model: Any, attr: str):
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

    def _create_file_dict(self, file, attr_name: str):
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

    def get_file_url(self, model: Any, **kwargs) -> str:
        """
        Example::

            file_upload.get_file_url(blog_post, filename="placeholder_img")
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
            self.file_data.append(self._create_file_dict(v, k))
        return self.file_data

    def _set_model_attrs(self, model: Any) -> None:
        """
        :param model:
        :return: None
        """
        for d in self.file_data:
            for k, v in d.items():
                self._check_attrs(model, k)
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
    #:    Warning: These methods need to set members on the Model class
    #:    before we instantiate FileUtils()
        self._set_file_data(**kwargs)
        self._set_model_attrs(model)

        self.file_utils = FileUtils(model, self.config)

    #:    Save files to dirs
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

    #:    Set file_data
        self._set_file_data(**kwargs)
        self._set_model_attrs(model)

        self.file_utils = FileUtils(model, self.config)

    #:    Save files to dirs
        self._save_files_to_dir(model)

    #:    remove original files from directory
        for f in original_file_names:
            os.remove(f"{self.file_utils.get_stream_path(model.id)}/{f}")

    #:    if a db arg is provided then commit changes to db
        if db:
            db.session.add(model)
            db.session.commit()
            return None
        else:
            return model

