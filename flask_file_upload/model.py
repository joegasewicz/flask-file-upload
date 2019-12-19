"""
   Public SqlAlchemy class decorator

    meta:
        -
"""
from typing import List, Dict
from functools import update_wrapper


from ._model_utils import _ModelUtils


class Model:

    file_names: List[str] = []

    new_cols: List[Dict[str, str]] = []

    primary_key: str

    def __init__(self, _class):
        update_wrapper(self, super)
        self._class = _class

        _new_cols = []
        _file_names = []

        new_cols, file_names = _ModelUtils.get_attr_from_model(self._class, _new_cols, _file_names)
        _ModelUtils.set_columns(self._class, new_cols)
        _ModelUtils.remove_unused_cols(self._class, file_names)
        super(Model, self).__init__()

    def __call__(self, *args, **kwargs):
        return self._class(*args, **kwargs)
