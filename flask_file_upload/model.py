"""
   Public SqlAlchemy class decorator

    meta:
        -
"""
from typing import Any, List, Tuple, Dict, ItemsView, Set
from functools import update_wrapper

from .column import Column
from ._model_utils import _ModelUtils


class Model:

    file_names: List[str] = []

    new_cols: List[Dict[str, str]] = []

    keys: Tuple[str] = ("file_name", "file_type", "mime_type")

    primary_key: str

    def __init__(self, _class):
        update_wrapper(self, super)
        print("CALLED ________________")
        super(Model, self).__init__()
        self._class = _class()

    def __call__(self, *args, **kwargs):
        self.get_attr_from_model()
        self.set_columns()
        self.remove_unused_cols()
        return self._class(*args, **kwargs)

    def get_attr_from_model(self):
        """
        Adds values to new_cols & file_names so as not to
        change the size of the dict at runtime
        :return: None
        """
        for attr, value in self._class.__dict__.items():
            if isinstance(value, Column):
                self.new_cols.append(self.columns_dict(attr, value.db))
                self.file_names.append(str(attr))

    def set_columns(self) -> None:
        """
        Sets related file data to a SqlAlchemy Model
        :return:
        """
        for col_dict in self.new_cols:
            for k, v in col_dict.items():
                setattr(self._class, k, v)

    def remove_unused_cols(self):
        """
        Removes the original named attributes
        (this could be a good place to store
         metadata in a dict for example...)
        :return:
        """
        for col_name in self.file_names:
            delattr(self._class, col_name)

    def columns_dict(self, file_name: str, db) -> Dict[str, Any]:
        """
        :return: Dict[str, Any]
        """
        return _ModelUtils.create_keys(self.keys, file_name, db.Column(db.String))
