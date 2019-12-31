"""
    Helper class
"""
import os
import errno

from ._config import Config
from ._model_utils import _ModelUtils


class FileUtils:

    table_name: str

    model = None

    config: Config

    id: int

    def __init__(self, model, config: Config):
        self.config = config
        self.model = model
        self.id = _ModelUtils.get_primary_key(model)
        self.table_name = _ModelUtils.get_table_name(model)

    @staticmethod
    def allowed_file(filename, config: Config) -> bool:
        """
        :param filename:
        :param config:
        :return bool:
        """
        return "." in filename and \
            filename.rsplit(".", 1)[1].lower() in config.allowed_extensions

    def postfix_file_path(self, id: int, filename: str) -> str:
        """
        :param id:
        :param filename:
        :return str:
        """
        return f"/{self.table_name}/{id}/{filename}"

    def get_file_path(self, model_id: int, filename: str) -> str:
        """
        :param model_id:
        :param filename:
        :return str:
        """
        return os.path.join(f"{self.config.upload_folder}{self.postfix_file_path(model_id, filename)}")

    def save_file(self, file, model_id: int) -> None:
        """
        :param file:
        :param model_id:
        :return None:
        """
        file_path = self.get_file_path(model_id, file.filename)
        if not os.path.exists(os.path.dirname(file_path)):
            try:
                os.makedirs(os.path.dirname(file_path))
            except OSError as err:
                if err.errno != errno.EEXIST:
                    raise OSError("[FLASK_FILE_UPLOAD_ERROR]: Couldn't create file path: "
                                  f"{file_path}")
        file.save(file_path)

    def get_stream_path(self, model_id: int):
        return os.path.join(f"{self.config.upload_folder}/{self.table_name}/{model_id}")
