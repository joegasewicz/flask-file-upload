from typing import List


class Config:

    upload_folder: str

    allowed_extensions: List

    max_content_length: int

    def init_config(self, app):
        self.upload_folder = app.config.get("UPLOAD_FOLDER")
        self.allowed_extensions = app.config.get("ALLOWED_EXTENSIONS")
        self.max_content_length = app.config.get("MAX_CONTENT_LENGTH")

