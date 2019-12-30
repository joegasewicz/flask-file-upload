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
    db = None

    def __init__(self, db=None):
        self.db = db
