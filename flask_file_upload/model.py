"""
Flask-File-Upload (FFU) setup requires each SQLAlchemy model that wants to use
FFU library to be decorated with ``@file_upload.Model``.This will enable FFU
to update your database with the extra columns required to store
files in your database.
Declare your attributes as normal but assign a value of
``file_upload.Column()``. Example::

Full example::

   from my_app import db, file_upload

   @file_upload.Model
   class blogModel(db.Model):
       __tablename__ = "blogs"
       id = db.Column(db.Integer, primary_key=True)
       my_placeholder = file_upload.Column()
       my_video = file_upload.Column()
"""
from ._model_utils import _ModelUtils


def create_model(db):
    #: We pass the db instance here as ``_ModelUtils.get_attr_from_model``
    #: requires access to the SQLAlchemy object.
    class Model:

        def __new__(cls, _class=None, *args, **kwargs):
            """
            We create a new instance of Model with all the attributes of
            the wrapped SqlAlchemy Model class. this is because we cannot
            make a call to self.query = _class.query as this will then
            create a a new session (_class.query calls to a __get__ descriptor).
            :param _class: Is the wrapped SqlAlchemy model
            :param args: The first arg is the wrapped SqlAlchemy model if exists.
                This means the __call__ method is being called either because Model
                is decorating an SQLAlchemy model or it is being reference, ie calling
                a static method e.g. Blog.query.filter_by()
            :param kwargs:
            :return:
            """
            if not isinstance(args, tuple):
                # Model is being reference
                instance = super(Model, cls).__new__(args[0], *args, **kwargs)
            else:
                # Model is being instantiated
                instance = _class
            new_cols = []
            filenames = []
            new_cols_list, filenames_list = _ModelUtils.get_attr_from_model(instance, new_cols, filenames, db)
            # Add new attributes to the SQLAlchemy model
            _ModelUtils.set_columns(instance, new_cols_list)
            # The original model's attributes set by the user for files get removed here
            _ModelUtils.remove_unused_cols(instance, filenames_list)
            return instance

    return Model
