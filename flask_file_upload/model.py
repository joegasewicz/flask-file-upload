"""
   Public SQLAlchemy class decorator.
"""
from functools import update_wrapper


from ._model_utils import _ModelUtils


class Model:
    """
    Flask-File-Upload (FFU) setup requires each SQLAlchemy model that wants to use
    FFU library to be decorated with ``@file_upload.Model``.This will enable FFU
    to update your database with the extra columns required to store
    files in your database.
    Declare your attributes as normal but assign a value of
    ``file_upload.Column`` & pass the SQLAlchemy ``db`` instance:
    ``file_upload.Column(db)``. This is easy if you are using Flask-SQLAlchemy::

        from flask_SQLAlchemy import SQLAlchemy

        db = SQLAlchemy()

    Full example::

       from my_app import db, file_upload

       @file_upload.Model
       class blogModel(db.Model):
           __tablename__ = "blogs"
           id = db.Column(db.Integer, primary_key=True)

           # Your files -  Notice how we pass in the SQLAlchemy instance
           # or `db` to the `file_uploads.Column` class:

           my_placeholder = file_upload.Column(db)
           my_video = file_upload.Column(db)

    """

    def __new__(cls, _class=None, *args, **kwargs):
        """
        We create a new instance of Model with all the attributes of
        the wrapped SqlAlchemy Model class. this is because we cannot
        make a call to self.query = _class.query as this will then
        create a a new session (_class.query calls to a __get__ descriptor).
        """
        if isinstance(args, tuple):
            instance = _class
        else:
            instance = super(Model, cls).__new__(args[0], *args, **kwargs)
        new_cols = []
        filenames = []
        new_cols_list, filenames_list = _ModelUtils.get_attr_from_model(instance, new_cols, filenames)
        # Add new attributes to the SQLAlchemy model
        _ModelUtils.set_columns(instance, new_cols_list)
        # The original model's attributes set by the user for files get removed here
        _ModelUtils.remove_unused_cols(instance, filenames_list)
        return instance
