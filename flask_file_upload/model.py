"""
   Public SqlAlchemy class decorator.
"""
from functools import update_wrapper


from ._model_utils import _ModelUtils


class Model:
    """
    Flask-File-Upload (FFU) setup requires each SqlAlchemy model that wants to use
    FFU library to be decorated with ``@file_upload.Model``.This will enable FFU
    to update your database with the extra columns required to store
    files in your database.
    Declare your attributes as normal but assign a value of
    ``file_upload.Column`` & pass the SqlAlchemy ``db`` instance:
    ``file_upload.Column(db)``. This is easy if you are using Flask-SqlAlchemy::

        from flask_sqlalchemy import SqlAlchemy

        db = SqlAlchemy()

    Full example::

       from my_app import db, file_upload

       @file_upload.Model
       class blogModel(db.Model):
           __tablename__ = "blogs"
           id = db.Column(db.Integer, primary_key=True)

           # Your files -  Notice how we pass in the SqlAlchemy instance
           # or `db` to the `file_uploads.Column` class:

           my_placeholder = file_upload.Column(db)
           my_video = file_upload.Column(db)

    """

    def __init__(self, _class):
        """
        We set all our attributes in this __init__ method so that when SqlAlchemy's
        `create_all` method is evoked the model's attributes are set.
        :param _class:
        """
        update_wrapper(self, super)
        super(Model, self).__init__()

        self._class = _class

        new_cols = []
        filenames = []

        new_cols_list, filenames_list = _ModelUtils.get_attr_from_model(self._class, new_cols, filenames)
        # Add new attributes to the SqlAlchemy model
        _ModelUtils.set_columns(self._class, new_cols_list)
        # The original model's attributes set by the user for files get removed here
        _ModelUtils.remove_unused_cols(self._class, filenames_list)

    def __call__(self, *args, **kwargs):
        """
        When the wrapped class is instantiated , this method will be called
        with the wrapped constructor kwargs passed in - in this case it would
        be the user's model attribute values
        :param args:
        :param kwargs:
        :return:
        """
        return self._class(*args, **kwargs)
