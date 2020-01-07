from warnings import warn


class Column:
    """
    The Column class is used to define the file attributes on
    a SqlAlchemy class model.
    Column class can be used when an SQLAlchemy class
    is decorated with Model `flask_file_upload.Model`
    constructor::

        my_video = file_upload.Column()
    """
    def __init__(self, db=None):
        if db:
            warn(
                DeprecationWarning(
                    "FLASK-FILE-UPLOAD: Passing db to Column class is now not "
                    "not required. This will be removed in v0.1.0"
                )
            )
