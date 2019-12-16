"""
   Public SqlAlchemy class decorator
"""
from typing import Any, List, Tuple, Dict, ItemsView


class Column:

    def __init__(self, file_name, *args, **kwargs):
        self.file_name = file_name
        self.db = kwargs.get("db")

    def __call__(self, args, **kwargs):
        class Wrapped:
            file_name: str = self.file_name
            db = self.db

            def __init__(self, *args, **kwargs):
                self.set_columns()

            def set_columns(self) -> None:
                """
                :return:
                """
                for k, v in self.columns_dict():
                    setattr(self, k, v)

            def columns_dict(self) -> ItemsView[str, str]:
                """
                :return: ItemsView[str, str]
                """
                col_dict = {
                    f"{self.file_name}_file_name": self.db.Column(self.db.String),
                    f"{self.file_name}_mime_type": self.db.Column(self.db.String),
                    f"{self.file_name}_file_type": self.db.Column(self.db.String),
                }
                return col_dict.items()

        return Wrapped
