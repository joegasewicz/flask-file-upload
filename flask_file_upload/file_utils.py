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

    def __init__(self, model, config: Config, **kwargs):
        self.config = config
        self.model = model
        self.id = kwargs.get("id") or "id"
        self.table_name = kwargs.get("table_name")

    @staticmethod
    def allowed_file(filename, config: Config) -> bool:
        return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in config.allowed_extensions

    def postfix_file_path(self, id: int, filename: str):
        return f"/{self.table_name}/{id}/{filename}"

    def get_file_path(self, id: int, filename: str):
        return os.path.join(f"{self.config.upload_folder}{self.postfix_file_path(id, filename)}")

    def save_file(self, file, id: int):
        """
        :param file:
        :param id:
        :return:
        """
        file.save(self.get_file_path(id, file.filename))
