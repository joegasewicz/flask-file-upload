"""
   Public SqlAlchemy class decorator
"""


class Column:

    def __init__(self, file_name, *args, **kwargs):
        self.file_name = file_name

    def __call__(self, args, **kwargs):
        class Wrapped:
            file_name: str = self.file_name

            def __call__(self, *args, **kwargs):
                pass

        return Wrapped

    def set_column(self, name, column_value) -> None:
        """
        :param name:
        :param column_value:
        :return:
        """
        setattr(self, name, column_value)
