"""
    Behaviours required by Model class _so we can keep SqlAlchemy Model
    free of methods & other members.
"""
from typing import List, Any, Dict, Tuple, ClassVar

from .column import Column


class _ModelUtils:

    keys: Tuple[str] = ("file_name", "file_type", "mime_type")

    @staticmethod
    def create_keys(keys: Tuple[str], filename: str, value: Any = None) -> Dict[str, None]:
        col_dict = {}
        for k in keys:
            col_dict[f"{filename}__{k}"] = value
        return col_dict

    @staticmethod
    def get_primary_key(model):
        """
        This will always target the first primary key in
        the list (in case there are multiple being used)
        :param model:
        :return:
        """
        if hasattr(model, "__mapper__"):
            return model.__mapper__.primary_key[0].name

    @staticmethod
    def get_table_name(model: Any) -> str:
        """
        Set on class initiation
        :return: None
        """
        return model.__tablename__

    @staticmethod
    def get_id_value(model) -> int:
        """
        :param model:
        :return:
        """
        return getattr(model, _ModelUtils.get_primary_key(model), None)

    @staticmethod
    def columns_dict(file_name: str, db) -> Dict[str, Any]:
        """
        :return: Dict[str, Any]
        """
        return _ModelUtils.create_keys(_ModelUtils.keys, file_name, db.Column(db.String))

    @staticmethod
    def set_columns(wrapped: ClassVar, new_cols: Tuple[Dict[str, Any]]) -> None:
        """
        Sets related file data to a SqlAlchemy Model
        :return:
        """
        for col_dict in new_cols:
            for k, v in col_dict.items():
                setattr(wrapped, k, v)

    @staticmethod
    def remove_unused_cols(wrapped: ClassVar,  filenames: Tuple[str]) -> None:
        """
        Removes the original named attributes
        (this could be a good place to store
         metadata in a dict for example...)
        :return:
        """
        for col_name in filenames:
            delattr(wrapped, col_name)

    @staticmethod
    def get_attr_from_model(wrapped: ClassVar, new_cols: List, file_names: List) -> Any:
        """
        Adds values to new_cols & file_names so as not to
        change the size of the dict at runtime
        :return None:
        """
        for attr, value in wrapped.__dict__.items():
            if isinstance(value, Column):
                new_cols.append(_ModelUtils.columns_dict(attr, value.db))
                file_names.append(str(attr))
        return new_cols, file_names

    @staticmethod
    def get_by_postfix(filename: str, file_type: str):
        return f"{filename}__{file_type}"
