"""
Flask File Upload Custom Exception
"""


class FlaskInstanceOrSqlalchemyIsNone(Exception):
    message = "You must pass your Flask app instance and " \
              "the SqlAlchemy instance to FileUpload class or" \
              "the init_app method. See https://flask-file-upload.readthedocs.io/en/latest/file_upload.html"

    def __init__(self, err=""):
        super(FlaskInstanceOrSqlalchemyIsNone, self).__init__(f"{err}\n{self.message}")
