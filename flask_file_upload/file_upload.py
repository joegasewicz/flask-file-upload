"""
FileUpload Class
================
"""
import os
from warnings import warn
from flask import send_from_directory, Flask, request, url_for
from werkzeug.utils import secure_filename
from typing import Any, List, Dict, Union

from ._config import Config
from .model import create_model
from .column import Column
from .file_utils import FileUtils
from ._model_utils import _ModelUtils


class FileUpload:
    """
    :param app: The Flask application instance: ``app = Flask(__name__, static_folder="uploads")``.
    :kwargs:
    :key allowed_extensions: A list of accepted file types eg. ['.jpg', etc..]
    :key upload_folder: where the uploaded files are stored
    :key max_content_length: Limit the amount of file memory
    :key sqlalchemy_database_uri: The database URI that should be used for the connection
    """

    #: Flask-File-Upload (**FFU**) requires Flask application configuration variables
    #: passed directly to the ``FileUpload`` class. This is because **FFU** needs to do some
    #: work on your SqlAlchemy models before the application instance is created. One
    #: way to make this setup dynamic, is to create your environment variables before
    #: creating a ``FileUpload`` instance & if any of these variables need to get
    #: reset dynamically when the Flask application instance is returned (*when using the
    #: factory-pattern*), then update them within the *create_app* function.
    #:
    #: We can then call the ``file_upload.init_app`` method & this will now receive the dynamically set
    #: variables. For Example::
    #:
    #:    app = Flask(__name__, static_folder="uploads")
    #:
    #:    db = SQLAlchemy()`
    #:
    #:    # Environment variables
    #:    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    #:    UPLOAD_FOLDER = join(dirname(realpath(__file__)), "uploads")
    #:    ALLOWED_EXTENSIONS = ["jpg", "png", "mov", "mp4", "mpg"]
    #:    MAX_CONTENT_LENGTH = 1000 * 1024 * 1024  # 1000mb
    #:    SQLALCHEMY_DATABASE_URI = "postgresql://localhost:5432/blog_database"
    #:
    #:    file_upload = FileUpload(
    #:        app,
    #:        db,
    #:        upload_folder=UPLOAD_FOLDER,
    #:        allowed_extensions=ALLOWED_EXTENSIONS,
    #:         max_content_length=MAX_CONTENT_LENGTH,
    #:         sqlalchemy_database_uri=SQLALCHEMY_DATABASE_URI,
    #:    )
    #:
    #:    # An example using the Flask factory pattern
    #:    def create_app():
    #:
    #:      # Dynamically set config variables:
    #:      app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    #:      app.config["ALLOWED_EXTENSIONS"] = ALLOWED_EXTENSIONS
    #:      app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
    #:      app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    #:
    #:      file_upload.init_app(app, db)
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

    #: The Flask-SQLAlchemy `SQLAlchemy()` instance`
    _db = None

    def __init__(self, app=None, db=None, *args, **kwargs):
        """
        :param app: The Flask application instance: ``app = Flask(__name__, static_folder="uploads")``.
        :param kwargs:
            :key allowed_extensions: A list of accepted file types eg. ['.jpg', etc..]
            :key upload_folder: where the uploaded files are stored
            :key max_content_length: Limit the amount of file memory
            :key sqlalchemy_database_uri: The database URI that should be used for the connection
        """
        self.Model = create_model(db)
        self.Column = Column
        if app:
            self.init_app(app, db, **kwargs)

    def add_file_urls_to_models(self, models, **kwargs):
        """
        The majority of requests will require many entities to be returned
        & these entities may have SQLAlchemy `backrefs` & these back reference
        relationships may also contain Flask-File-Upload (FFU) modified SQLAlchemy
        models. To make this trivial, this method will set the appropriate
        filename urls to to your SQLAlchemy model object (if the transaction
        hasn't completed then **add_file_urls_to_models** will complete the
        transaction by default).

        The the only argument is `models` the SQLAlchemy model (which is is
        normally many but can be a single item from your table.

        Then pass in the required kwarg `filenames` which references the parent(s)
        FFU Model values - this is the `file_upload.Model` decorated SQLALchemy model
        - `file_upload.Column()` method.

        Important! Also take note that each attribute set by this method postfixes
        a `_url` tag. e.g `blog_image` becomes `blog_image_url`

        Example for many SQLAlchemy entity objects (*or rows in your table*)::

            @file_upload.Model
            class BlogModel(db.Model):

                blog_image = file_upload.Column()

        Now we can use the `file_upload.add_file_urls_to_models` to add file urls to
        each SQLAlchemy object. For example::

            blogs = add_file_urls_to_models(blogs, filenames="blog_image")

            # Notice that we can get the file path `blog_image` + `_url`
            assert  blogs[0].blog_image_url == "path/to/blogs/1/blog_image.png"

        To set filename attributes to multiple SQLAlchemy parent models with backrefs
        to multiple child SQLAlchemy models, we can assign to the optional `backref`
        kwarg the name of the backref model & a list of the file attributes we set
        with the FFU Model decorated SQLAlchemy model.

        To use backrefs we need to declare a kwarg of `backref` & pass 2 keys:
            - **name**: The name of the backref relation
            - **filenames**: The FFU attribute values assigned to the backref model

        For example::

            # Parent model
            @file_upload.Model
            class BlogModel(db.Model):
                # The backref:
                blog_news = db.relationship("BlogNewsModel", backref="blogs")
                blog_image = file_upload.Column()
                blog_video = file_upload.Column()

            # Model that has a foreign key back up to `BlogModel
            @file_upload.Model
            class BlogNewsModel(db.Model):
                # The foreign key assigned to this model:
                blog_id = db.Column(db.Integer, db.ForeignKey("blogs.blog_id"))
                news_image = file_upload.Column()
                news_video = file_upload.Column()

        The kwarg `backref` keys represent the backref model or entity (in the above example
        this would be the `BlogNewsModel` which we have named `blog_news`. Example::

            blogs = add_file_urls_to_models(blogs, filenames=["blog_image, blog_video"],
                backref={
                    "name": "blog_news",`
                    "filenames": ["news_image", "news_video],
            })

        WARNING: You must not set the relationship kwarg: `lazy="dynamic"`!
        If `backref` is set to *"dynamic"* then back-referenced entity's
        filenames will not get set. Example::

            # This will work
            blog_news = db.relationship("BlogNewsModel", backref="blog")

            # this will NOT set filenames on your model class
            blog_news = db.relationship("BlogNewsModel", backref="blog", lazy="dynamic")


        :param models: SQLAlchemy models (this must be many entities)
        :key filename: The Parent models. This can be a single string or a list of strings
        :kwargs backref:
            - **name**: The name of the backref relation
            - **filenames**: The FFU attribute value assigned to this model This can be a \
            single string or a list of strings

        :return: A list or nested list of SQLAlchemy Model objects.
        """
        filenames = kwargs.get("filenames")
        backref = kwargs.get("backref")
        backref_name = None
        backref_filenames = None
        if backref:
            try:
                backref_name = backref["name"]
                backref_filenames = backref["filenames"]
                if not isinstance(filenames, list):
                     filenames = [filenames]
                if not isinstance(backref_filenames, list):
                    backref_filenames = [backref_filenames]
            except TypeError:
                raise TypeError(
                    "Flask-File_Upload Error: If `backref` kwarg is declared "
                    "then you must include `filenames` & `name` keys. See "
                    "https://github.com/joegasewicz/flask-file-upload"
                )

        _models = []
        try:
            _models = models.all()
        except:
            _models = models
        if not backref:
            for model in _models:
                for filename in filenames:
                    model_img_url = self.get_file_url(model, filename=filename)
                    setattr(model, f"{filename}_url", model_img_url)
            return _models
        else:
            for model in _models:
                for filename in filenames:
                    model_img_url = self.get_file_url(model, filename=filename)
                    setattr(model, f"{filename}_url", model_img_url)
                    backref_models = getattr(model, backref_name)
                    for backref_filename in backref_filenames:
                        if backref and backref_models:
                            for br_model in backref_models:
                                br_model_img_url = self.get_file_url(br_model, filename=backref_filename)
                                setattr(br_model, f"{backref_filename}_url", br_model_img_url)
            return _models

    def delete_files(self, model: Any, db=None, **kwargs) -> Union[Any, None]:
        """
        Public method for removing stored files from the server & database.
        This method will remove all files passed to the kwarg ``files`` list
        from the server. It will also update the passed in SqlAlchemy ``model``
        object & return the updated model.

        If `commit` kwarg has not been set then the session is updated & session commited &
        this method returns the current updated model

        *If a current session exists then Flask-File-Upload will use this before attempting to
        create a new session*.
        Example::

            # Example using a SqlAlchemy model with an appended
            # method that fetches a single `blog`
            blogModel = BlogModel()
            blog_results = blogModel.get_one()

            # We pass the blog & files
            blog = file_upload.delete_files(blog_result, commit=False, files=["my_video"])

            # As the `commit` kwarg has been set to False,
            # the changes would need persisting to the database:
            db.session.add(blog)
            db.session.commit()

            # If `commit` kwarg is not set (default is True) then the updates are persisted.
            # to the session. And therefore the session has been commited.
            blog = file_upload.delete_files(blog_result, files=["my_video"])


        :param model: Instance of a SqlAlchemy Model
        :key files: A list of the file names declared on your model.
        :key commit: Default is set to True. If set to False then the changed to the
            model class will not be updated or commited.
        :key clean_up: Default is None. There are 2 possible ``clean_up`` values
        you can pass to the ``clean_up`` kwarg:
            - ``files`` will clean up files on the server but not update the model
            - ``model`` will update the model but not attempt to remove the files
                from the server.

        Example::

            # To clean up files on your server pass in the args as follows:
            file_upload.delete_files(blog_result, files=["my_video"], clean_up="files")

            # To clean up the model pass in the args as follows:
            file_upload.delete_files(blog_result, files=["my_video"], clean_up="model")

        The root directory (*The directory containing the files*) which is named after the model
        id, is never deleted. Only the files within this directory are removed from the server.

        :return: SqlAlchemy model object
        """
        try:
            files: List[str] = kwargs["files"]
        except KeyError:
            warn("'files' is a Required Argument")
            return None

        if db:
            warn(
                DeprecationWarning(
                    "FLASK-FILE-UPLOAD: Passing `db` as a second argument  to `update_files` method. "
                    "is now not required. The second argument to `update_files` method will be "
                    "removed in version v0.1.0"
                )
            )

        self.file_utils = FileUtils(model, self.config)

        clean_up = kwargs.get("clean_up")
        commit = kwargs.get("commit") or True

        primary_key = _ModelUtils.get_primary_key(model)
        model_id = getattr(model, primary_key, None)

        if clean_up is None or clean_up is "files":
            for f in files:
                original_filename = _ModelUtils.get_original_file_name(f, model)
                file_path = f"{self.file_utils.get_stream_path(model_id)}/{original_filename}"
                os.remove(f"{file_path}")

        if clean_up is None or clean_up is "model":
            for f_name in files:
                for postfix in _ModelUtils.keys:
                    setattr(model, _ModelUtils.add_postfix(f_name, postfix), None)
            return _ModelUtils.commit_session(self.db, model, commit)
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

    def  _clean_up(self, error) -> None:
        """Clean list data & state"""
        self.files.clear()
        self.file_data.clear()

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
        Returns the url path to a file on your server.
        To access the file, it must reference the attribute name
        defined on your SqlAlchemy model. For example::

            @file_upload.Model
            class ModelTest(db.Model):

                my_video = file_upload.Column()

        To return the url of the above file, pass in attribute name
        to the ``filename`` kwarg. Example::

            file_upload.get_file_url(blog_post, filename="my_video")

        :param model:
        :param kwargs:
        :return:
        """
        try:
            filename = kwargs["filename"]
            self.file_utils = FileUtils(model, self.config)

            primary_key = _ModelUtils.get_primary_key(model)
            model_id = getattr(model, primary_key, None)
            file_name = _ModelUtils.get_by_postfix(model, filename, "file_name")
            file_path = self.file_utils.postfix_file_path(model_id, file_name)

            url_root = request.url_root
            if url_root[-1] == "/":
                url_root = url_root[:-1]

            image_path = url_for('static', filename=file_path).replace("//", "/")
            if image_path[0] == "/":
                image_path = image_path[1:]
            if filename:
                return f"{url_root}/{image_path}"
        except AttributeError:
            AttributeError("[FLASK_FILE_UPLOAD] You must declare a filename kwarg")

    def init_app(self, app, db=None, **kwargs) -> None:
        """
        If you are using the Flask factory pattern, normally you
        will, by convention, create a method called ``create_app``.
        At runtime, you may then set configuration values before initiating
        FileUpload etc. Example::

            app = Flask(__name__, static_folder="uploads/media")
            file_upload = FileUpload()

            def create_app():
                file_upload.init_app(app, db)

        :param app: The Flask application instance: ``app = Flask(__name__, static_folder="uploads")``.
        :return: None
        """
        # Let Flask request hook handle calling `self._clean_up`
        @app.teardown_request
        def _cu(_):
            self._clean_up(error=None)

        db = db or self.db
        self.app = app
        self.config.init_config(app, **kwargs)
        self._db = db
        if db:
            app.extensions["file_upload"] = {
                "db": db,
            }

    def save_files(self, model, **kwargs) -> Any:
        """
        The file(s) must reference the attribute name(s)
        defined in your SqlAlchemy model. For example::

            @file_upload.Model
            class ModelTest(db.Model):

                my_video = file_upload.Column()
                placeholder_img = file_upload.Column()

        This example demonstrates creating a new row in your database
        using a SqlAlchemy model which is is then pass as the first
        argument to ``file_upload.save_files``. Normally, you will
        access your files from Flask's ``request`` object::

            from Flask import request

            my_video = request.files['my_video']
            placeholder_img = request.files['placeholder_img']

        Then, we need to pass to the kwarg ``files`` a dict of keys that
        reference the attribute name(s) defined in your SqlAlchemy
        model & values that are your files.::

            blog_post = BlogPostModel(title="Hello World Today")

            file_upload.save_files(blog_post, files={
                "my_video": my_video,
                "placeholder_img": placeholder_img,
            })

        :param model: The SqlAlchemy model instance
        :key filename: The attribute name(s) defined in your SqlAlchemy model
        :key commit_session: Default is `True` or if you have not passed in
        a SQLAlchemy instance to ``FileUpload()`` then it is also set to False.
        *If you prefer to handle the session yourself*.

        :return: The updated SqlAlchemy model instance
        """
        # Warning: These methods need to set members on the Model class
        # before we instantiate FileUtils()
        self._set_file_data(**kwargs)
        self._set_model_attrs(model)

        self.file_utils = FileUtils(model, self.config)

        commit_session = kwargs.get("commit_session") or True
        model = _ModelUtils.commit_session(self.db, model, commit_session)
        self._save_files_to_dir(model)
        return model

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
        :return:  List[Dict[str, str]]
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
        the Flask's ``UPLOAD_FOLDER``, in your Flask app's
        configuration settings. To access the file,
        it must reference the attribute name defined on
        your SqlAlchemy model. For example::

            @file_upload.Model
            class ModelTest(db.Model):

                my_video = file_upload.Column()

        The required steps to stream files using ``file_upload.stream_file`` are:

        1. Fetch the required row from your database using SqlAlchemy::

            blog = BlogModel.query.filter_by(id=id).first()

        2. Pass the SqlAlchemy instance to ``file_upload.stream_file`` &
           reference the attribute name defined on your SqlAlchemy model::

            file_upload.stream_file(blogs, filename="my_video")

        :param model: SqlAlchemy model instance.
        :key filename: The attribute name defined on your SqlAlchemy model
        :return: Updated SqlAlchemy model instance or None.
        """
        try:
            filename = kwargs['filename']
        except KeyError:
            warn("'files' is a Required Argument")
            return None

        self.file_utils = FileUtils(model, self.config)
        primary_key = _ModelUtils.get_primary_key(model)
        model_id = getattr(model, primary_key, None)
        return send_from_directory(
            self.file_utils.get_stream_path(model_id),
            _ModelUtils.get_original_file_name(filename, model),
            conditional=True,
        )

    def update_files(self, model: Any, db=None, **kwargs):
        """
        First reference the attribute name defined on your
        SqlAlchemy model. For example::

            @file_upload.Model
            class ModelTest(db.Model):

                my_video = file_upload.Column()

        Pass the model instance as a first argument to ``file_upload.update_files``.
        The kwarg ``files`` requires the file(s) returned from Flask's request body::

            from Flask import request

            my_video = request.files['my_video']
            placeholder_img = request.files['placeholder_img']

        Then, we need to pass to the kwarg ``files`` a dict of keys that
        reference the attribute name(s) defined in your SqlAlchemy
        model & values that are your files.::


            blog_post = BlogPostModel(title="Hello World Today")
            blog_post = file_upload.update_files(blog_post, files={
                "my_video": new_my_video,
                "placeholder_img": new_placeholder_img,
            })

        :param model: SqlAlchemy model instance.
        :key files Dict[str, Any]: A dict with the key representing the model attr
             name & file as value.
        :key commit: Default is True which is recommended. If commit is False,
            then only the files on the server are removed & the model is updated with
            each attribute set to None but the session is not commited (This could cause
            your database & files on server to be out of sync if you fail to commit
            the session.
        :return Any: Returns the model back
        """
        try:
            files = kwargs["files"]
        except KeyError:
            warn("'files' is a Required Argument")
            return None

        commit = kwargs.get("commit") or True

        if db:
            warn(
                DeprecationWarning(
                    "FLASK-FILE-UPLOAD: Passing `db` as a second argument  to `update_files` method. "
                    "is now not required. The second argument to `update_files` method will be "
                    "removed in version v0.1.0"
                )
            )

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
            primary_key = _ModelUtils.get_primary_key(model)
            model_id = getattr(model, primary_key, None)
            # If the model is updated later with file attributes the file path
            # then has not yet been created, so we do not have to remove the old
            # files etc:
            try:
                os.remove(f"{self.file_utils.get_stream_path(model_id)}/{f}")
            except FileNotFoundError:
                pass

        return _ModelUtils.commit_session(self.db, model, commit)

    @property
    def db(self):
        if self._db:
            return self._db
        else:
            try:
                self.app.extensions["file_upload"].get("db")
            except (AttributeError, KeyError):
                raise(
                    "FLASK-FILE-UPLOAD: You must pass an instance of SQLAlchemy to "
                    "`FileUpload(app, db)` or `file_upload.init_app(app, db)` as a "
                    "second argument."
                )

    @db.setter
    def db(self, db):
        self._db = db
