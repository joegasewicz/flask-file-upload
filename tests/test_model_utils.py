from flask_file_upload._model_utils import _ModelUtils
from tests.fixtures.models import MockBlogModel


class Test_FileUtils:

    def test_create_keys(self):
        result = {
            "my_video__file_name": None,
            "my_video__mime_type": None,
            "my_video__file_type": None,
        }

        assert result == _ModelUtils.create_keys(_ModelUtils.keys, "my_video")

    def test_get_by_postfix(self):
        test_model = MockBlogModel()
        assert hasattr(test_model, _ModelUtils.get_by_postfix("my_video", _ModelUtils.keys[1]))
