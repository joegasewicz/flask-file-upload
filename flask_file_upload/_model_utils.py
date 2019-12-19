"""
    Behaviours required by Model class _so we can keep SqlAlchemy Model
    free of methods & other members.
"""
from typing import List, Any, Dict, Tuple


class _ModelUtils:

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
