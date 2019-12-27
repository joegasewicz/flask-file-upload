from typing import List
from warnings import warn


class Config:

    upload_folder: str = ""

    server_name: str = ""

    allowed_extensions: List = []

    max_content_length: int = 0

    def init_config(self, app):
        self.server_name = app.config["SERVER_NAME"]
        try:
            self.upload_folder = app.config["UPLOAD_FOLDER"]
        except KeyError as _:
            raise KeyError("Flask-File-Uploads: UPLOAD_FOLDER must be set")
        try:
            self.allowed_extensions = app.config["ALLOWED_EXTENSIONS"]
        except KeyError as _:
            self.allowed_extensions = ["jpg", "png", "mov", "mp4", "mpg"]
            warn("Flask-File-Uploads: ALLOWED_EXTENSIONS is not set."
                 f"Defaulting to: {self.allowed_extensions}")
        self.max_content_length = app.config.get("MAX_CONTENT_LENGTH")
