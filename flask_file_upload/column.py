from warnings import warn


class Column:
    """
    The Column class is used to define the file attributes on
    a SqlAlchemy class model.
    """
    #: If Flask-SqlAlchemy is used then create an instance of the
    #: SqlAlchemy class and then pass this instance to the Column
    #: constructor::
    #:
    #:      from flask_sqlalchemy import SQLAlchemy
    #:
    #:      db = SQLAlchemy()
    #:      my_video = file_upload.Column(db)

    def __init__(self, db=None):
        if db:
            warn(
                DeprecationWarning(
                    "FLASK-FILE-UPLOAD: Passing db to Column class is now not "
                    "not required. This will be removed in v0.1.0"
                )
            )
