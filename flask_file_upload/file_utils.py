"""
    Helper class
"""
import os

from ._config import Config


class FileUtils:

    table_name: str

    model = None

    config: Config

    id: int

    def __init__(self, model, config, **kwargs):
        self.config = config
        self.model = model
        self.id = kwargs.get("id")
        self.table_name = kwargs.get("table_name")

    def allowed_file(self, filename):
        return "." in filename and \
            filename.rsplit(".", 1)[1].lower() in self.config.allowed_extensions

    def get_file_root_path(self):
        return f'{os.path.join(self.config.upload_folder)}'

    def postfix_file_path(self, id: int, filename: str):
        return f"/{self.table_name}/{id}/{filename}"

    def get_file_path(self, id: int, filename: str):
        return f"{self.get_file_root_path()}{self.postfix_file_path(id, filename)}"

    def save_file(self, file, id: int, filename):
        file.save(self.get_file_path(id, filename))
