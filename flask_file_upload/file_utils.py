"""
    Helper class
"""
import os

from ._config import Config

class FileUtils:

    table_name: str

    model = None

    config: Config

    def __init__(self, model, config):
        self.config = config
        self.model = model
        self.set_table_name()

    def set_table_name(self) -> None:
        """
        Set on class initiation
        :return: None
        """
        self.table_name = self.model.__tablename__

    def get_file_root_path(self):
        return f'{os.path.join(self.config.upload_folder)}'

    def postfix_file_path(self):
        return f"{self.get_file_root_path()}/"

    def save_file(self, file, config):
        file.save(os.path.join(config["UPLOAD_FOLDER"]))