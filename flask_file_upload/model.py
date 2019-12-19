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
        """
        We set all our attributes in this __init__ method so that when SqlAlchemy's
        `create_all` method is evoked the model's attributes are set.
        :param _class:
        """
        update_wrapper(self, super)

        self._class = _class

        new_cols = []
        filenames = []

        new_cols_list, filenames_list = _ModelUtils.get_attr_from_model(self._class, new_cols, filenames)
        _ModelUtils.set_columns(self._class, new_cols_list)
        _ModelUtils.remove_unused_cols(self._class, filenames_list)

        super(Model, self).__init__()

    def __call__(self, *args, **kwargs):
        """
        When the wrapped class is instantiated , this method will be called
        with the wrapped constructor kwargs passed in - in this case it would
        be the user's model attribute values
        :param args:
        :param kwargs:
        :return:
        """
        return self._class(*args, **kwargs)
